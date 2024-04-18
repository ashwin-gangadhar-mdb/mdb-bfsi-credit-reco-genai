from pymongo import MongoClient
import certifi

from langchain_fireworks import Fireworks 
from openai import OpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain.embeddings import HuggingFaceInstructEmbeddings
from langchain.retrievers import MultiQueryRetriever

from prompt_utils import get_credit_score_expl_prompt, get_credit_card_recommendations_prompt, user_profile_based_cc_rec_prompt

from dotenv import load_dotenv

load_dotenv()

import os
from functools import lru_cache

MONGO_CONN=os.environ.get("MONGO_CONNECTION_STRING")
client = MongoClient(MONGO_CONN,tlsCAFile=certifi.where())
vcol = client["bfsi-genai"]["cc_products"]

# llm = Fireworks(
#     fireworks_api_key=os.environ.get("FIREWORKS_API_KEY"),
#     model="accounts/fireworks/models/mistral-7b-instruct-v0p2",
#     temperature=0.2, 
#     max_tokens=4096, 
#     top_p=1.0, 
#     top_k=40
#     )

llm = Fireworks(
    fireworks_api_key=os.environ["FIREWORKS_API_KEY"],
    model="accounts/fireworks/models/mixtral-8x7b-instruct",
    base_url="https://api.fireworks.ai/inference/v1/completions",
    max_tokens=4096,
    temperature=0.2,
    top_p=1,
    top_k=40
)

# embedding model
repo_id = "hkunlp/instructor-base"
hf = HuggingFaceInstructEmbeddings(model_name=repo_id, cache_folder="tmp/")
hf.embed_instruction = "Represent the document for retrieval of personalized credit cards:"

# Vector store declaration
vectorstore = MongoDBAtlasVectorSearch(vcol, hf)
retriever = vectorstore.as_retriever(search_type='similarity',search_kwargs={'k': 1})
recommender_retriever = MultiQueryRetriever.from_llm(retriever=retriever,llm=llm)

@lru_cache(1000000)
def invoke_llm(prompt):
    """
    Invoke the LLM with the given prompt with cache.

    Args:
        prompt (str): The prompt to pass to the LLM.
    """
    response = llm.invoke(prompt)
    return response

def get_credit_score_expl(user_profile_ip, pred, allowed_credit_limit, feature_importance):
    """
    
    Get the credit score explanation from the LLM.

    Args:
        user_profile_ip (str): The user profile information.
        pred (float): The predicted credit score.
        allowed_credit_limit (float): The allowed credit limit.
        feature_importance (dict): The feature importance dictionary for the used ML model.

    """
    prompt = get_credit_score_expl_prompt.format(user_profile_ip=user_profile_ip, \
                                                 pred=pred, \
                                                 allowed_credit_limit=allowed_credit_limit, \
                                                 feature_importance=feature_importance)
    return invoke_llm(prompt)

@lru_cache(1000)
def get_credit_card_recommendations(user_profile, user_profile_ip, pred, allowed_credit_limit, card_suggestions):
    """
    
    Get the credit card recommendations from the LLM.

    Args:
        user_profile (str): The user profile information.
        user_profile_ip (json): The user profile information in Json format.
        pred (float): The predicted credit score.
        allowed_credit_limit (float): The allowed credit limit.
        card_suggestions (str): The card suggestions string.

    """
    prompt = get_credit_card_recommendations_prompt.format(user_profile=user_profile,\
                                                  user_profile_ip=user_profile_ip,\
                                                  pred=pred,\
                                                  allowed_credit_limit=allowed_credit_limit,\
                                                  card_suggestions=card_suggestions)
    return invoke_llm(prompt)

@lru_cache(1000)
def get_product_suggestions(user_profile, user_profile_ip, pred, allowed_credit_limit) -> str:
    """

    Get the product suggestions from the LLM.

    Args:
        user_profile (str): The user profile information.
        user_profile_ip (str): The user profile information in Json format.
        pred (float): The predicted credit score.
        allowed_credit_limit (float): The allowed credit limit.

    """
    search_term_suggestions = ["User profiles with Good Credit Health should be recommended cards with higher credit limit and better features, search with words like premium, exclusive, and luxury, ultra",\
                              "User profiles with Poor Credit Health should be recommended cards with lower credit limit and basic features, search with words like basic, advantage, cashback, budget, low interest, and low fees",\
                              "User profiles with Standard Credit Health should be recommended cards with moderate credit limit and features"]

    if pred=='Good':
        search_term_suggestion = search_term_suggestions[0]
    elif pred=='Poor':
        search_term_suggestion = search_term_suggestions[1]
    elif pred=='Standard':
        search_term_suggestion = search_term_suggestions[2]

    prompt = user_profile_based_cc_rec_prompt.format(user_profile=user_profile, \
                                                    user_profile_ip=user_profile_ip, \
                                                    pred=pred, \
                                                    allowed_credit_limit=allowed_credit_limit,
                                                    search_term_suggestion=search_term_suggestion)
    rec = recommender_retriever.get_relevant_documents(prompt, kwargs={"k":1})
    card_suggestions= ""
    for r in rec:
        card_suggestions += f'- Card name:{" ".join(r.metadata["title"].split("-"))} card \n  Card Features:{r.page_content} +\n'
    return card_suggestions

