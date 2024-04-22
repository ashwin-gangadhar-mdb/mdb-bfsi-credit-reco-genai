import os
import logging
import certifi
from datetime import datetime
from functools import lru_cache
from typing import Any, Dict

from pymongo import MongoClient
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.mongodb import MongoDBSaver

from dummy import PrepareDummyCols
from credit_rating import get_user_profile, get_model_feature_imps
from credit_score_expl import get_credit_score_expl
from credit_product_recommender import (
    get_credit_card_recommendations,
    get_final_user_profile_cc_rec,
)
from utils import CCrecommenderState
from mdb_utils import get_mongo_client, DB_NAME, COLLECTION_NAME

# ─── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)



def insert_response(doc: Dict[str, Any]) -> None:
    client = get_mongo_client()
    collection = client[DB_NAME][COLLECTION_NAME]
    collection.update_one({"user_id": doc["user_id"]}, {"$set": doc}, upsert=True)
    logger.info(f"Inserted/Updated document for user_id: {doc['user_id']}")
    logger.info(f"Document: {doc}")

def check_if_user_exists(state) -> str:
    """Check if the user exists in the database."""
    user_id = state["user_id"]
    client = get_mongo_client()
    collection = client[DB_NAME][COLLECTION_NAME]
    user = collection.find_one({"user_id": user_id})
    pred, _, _ = get_user_profile(user_id)
    if user and user.get("pred") == pred:
        logger.info(f"User {user_id} exists in the database.")
        return "recommendations"  # Proceed to the next step
    else:
        logger.info(f"User {user_id} does not exist in the database.")
        return "credit_profile"  # Proceed to create a new user profile

# ─── Business Logic Steps ───────────────────────────────────────────────────
def credit_rating_profile(state: CCrecommenderState) -> Dict[str, Any]:
    """Get the user profile, credit rating & explanations."""
    user_id = state["user_id"]
    pred, limit, raw_profile = get_user_profile(user_id)
    feat_imps = get_model_feature_imps()
    profile = get_credit_score_expl(
        raw_profile, pred, limit, feat_imps
    )

    insert_response({
        "user_id": user_id,
        "user_profile": profile,
        "user_profile_ip": raw_profile,
        "pred": pred,
        "allowed_credit_limit": limit,
    })
    logger.info(f"Inserted/Updated document for user_id: {user_id}")
    logger.info(f"Document: {{'user_id': {user_id}, 'user_profile': {profile}, 'user_profile_ip': {raw_profile}, 'pred': {pred}, 'allowed_credit_limit': {limit}}}")
    return {
        "pred": pred,
        "allowed_credit_limit": limit,
        "user_profile_ip": raw_profile,
        "user_profile": profile,
    }

def recommendations_step(state: CCrecommenderState) -> Dict[str, Any]:
    recs = get_credit_card_recommendations(
        user_profile=state["user_profile"],
        user_profile_ip=state["user_profile_ip"],
        pred=state["pred"],
        allowed_credit_limit=state["allowed_credit_limit"],
    )
    insert_response({
        "user_id": state["user_id"],
        "card_suggestions": recs.card_suggestions,
    })
    logger.info(f"Inserted/Updated document for user_id: {state['user_id']}")
    logger.info(f"Document: {{'user_id': {state['user_id']}, 'card_suggestions': {recs.card_suggestions}}}")
    return {"card_suggestions": recs.card_suggestions}

def rerank_step(state: CCrecommenderState) -> Dict[str, Any]:
    final = get_final_user_profile_cc_rec(
        user_profile=state["user_profile"],
        user_profile_ip=state["user_profile_ip"],
        pred=state["pred"],
        allowed_credit_limit=state["allowed_credit_limit"],
        card_suggestions=state["card_suggestions"],
    )
    insert_response({
        "user_id": state["user_id"],
        "final_recommendations": final.model_dump(),
    })
    return {"final_recommendations": final}

def validate_step(state: CCrecommenderState) -> Dict[str, Any]:
    """Validate & persist to MongoDB."""
    base_doc = {
        "user_id": state["user_id"],
        "timestamp": datetime.utcnow(),
    }

    if "final_recommendations" not in state:
        doc = {**base_doc, "response": "Recommendations invalid"}
        insert_response(doc)
        return {"response": doc["response"]}

    final = state["final_recommendations"]
    # handle pydantic or dict
    def serialize(card: Any) -> Any:
        return (
            card.model_dump()
            if hasattr(card, "model_dump")
            else card
        )

    serialized = [serialize(c) for c in final.cards]
    doc = {
        **base_doc,
        "response": "Recommendations valid",
        "final_recommendations": serialized,
        "user_profile": state["user_profile"],
        "user_profile_ip": state["user_profile_ip"],
        "pred": state["pred"],
        "allowed_credit_limit": state["allowed_credit_limit"], 
    }
    insert_response(doc)
    return {
        "response": doc["response"],
        "final_recommendations": final,
        "user_profile": state["user_profile"],
        "user_profile_ip": state["user_profile_ip"],
        "pred": state["pred"],
        "allowed_credit_limit": state["allowed_credit_limit"], 
    }

def should_end(state: CCrecommenderState) -> str:
    return END if state.get("response") else "recommendations"

# ─── App Factory ────────────────────────────────────────────────────────────
@lru_cache(maxsize=1)
def get_app():
    graph = StateGraph(CCrecommenderState)
    graph.add_node("check_user_exist", check_if_user_exists)
    graph.add_node("credit_profile", credit_rating_profile)
    graph.add_node("recommendations", recommendations_step)
    graph.add_node("rerank", rerank_step)
    graph.add_node("validate", validate_step)

    # graph.add_edge(START, "credit_profile")
    graph.add_conditional_edges(
        START,
        check_if_user_exists,
        ["credit_profile", "recommendations"],
    )
    graph.add_edge("credit_profile", "recommendations")
    graph.add_edge("recommendations", "rerank")
    graph.add_edge("rerank", "validate")    
    graph.add_conditional_edges(
        "validate",
        should_end,
        ["recommendations", END],
    )

    saver = MongoDBSaver(get_mongo_client())
    return graph.compile(checkpointer=saver)

# ─── Main ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    user_id = 8625
    inputs = {"user_id": user_id}
    config = {"recursion_limit": 15, "configurable": {"thread_id": user_id}}

    response = get_app().invoke(inputs, config=config)
    # for event in get_app().stream(inputs, config=config):
    #     for key, val in event.items():
    #         if key != "__end__":
    #             logger.info(val)
    #             response = val

    # print final output
    if response and "final_recommendations" in response:
        print("\n-- Cards --")
        for c in response["final_recommendations"].cards:
            print(c.model_dump_json())
        print("\n-- Profile --")
        print(response["user_profile"])
