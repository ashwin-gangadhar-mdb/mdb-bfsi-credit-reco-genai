import pandas as pd
import joblib
from pymongo import MongoClient
import certifi
import os
import json

import numpy as np

from dummy import PrepareDummyCols
from dotenv import load_dotenv
load_dotenv()
from functools import lru_cache

from llm_utils import invoke_llm, get_credit_score_expl, get_product_suggestions, get_credit_card_recommendations

import logging

MONGO_CONN=os.environ.get("MONGO_CONNECTION_STRING")
client = MongoClient(MONGO_CONN,tlsCAFile=certifi.where())
col = client["bfsi-genai"]["user_data"]

label_encoder_l = joblib.load("../model/credit_score_mul_lable_le.jlb")
dummy_l = joblib.load("../model/credit_score_mul_lable_coldummy.jlb")
model_l = joblib.load("../model/credit_score_mul_lable_model.jlb")
ordinal_enc_l = joblib.load("../model/credit_score_mul_lable_ordenc.jlb")

def predict(df):
    df_copy = df.copy()
    df_copy.drop(columns=["ID", "Customer_ID", "Name", "SSN","Credit_Score"], inplace=True)
    df_copy = dummy_l.transform(df_copy)
    df_copy[ordinal_enc_l.feature_names_in_] = ordinal_enc_l.transform(df_copy[ordinal_enc_l.feature_names_in_])
    v = model_l.predict_proba(df_copy[model_l.feature_names_in_])[0]
    pred = label_encoder_l.inverse_transform(model_l.predict(df_copy[model_l.feature_names_in_]))[0]
    return pred,v

def get_user_profile(user_id):
    logging.info(f"Processing User ID: {user_id}")
    user_id_df = pd.DataFrame.from_records((col.find({"Customer_ID":int(user_id)}, {"_id":0})))
    pred,v = predict(user_id_df)
    user_id_df.drop(columns=["ID", "Customer_ID", "SSN","Credit_Score"], inplace=True)
    user_profile_ip = user_id_df.to_dict(orient="records")[0]
    monthly_income = user_id_df.Monthly_Inhand_Salary
    logging.info(f">>>>>>>>>>>>>>>>>>>>>> Monthly Income : {monthly_income}")
    allowed_credit_limit = int(np.ceil(monthly_income*6*(1-(1*v[0]+0.5*v[1]+0.25*v[2]))))
    logging.info(f"Allowed Credit Limit for the user: {allowed_credit_limit}")
    return pred, allowed_credit_limit, user_profile_ip

@lru_cache(1)
def get_model_feature_imps():
    # model = joblib.load("classifier.jlb")
    df = pd.DataFrame.from_records((col.find({"Customer_ID":8625}, {"_id":0})))
    imp_idx = np.argsort(-1 * model_l.feature_importances_)
    feature_importance = "\n".join(i for i in list(map(lambda x:f"Columns:{x[0]}  Prob score for decision making:{x[1]}" ,zip(df.columns[imp_idx], model_l.feature_importances_[imp_idx]))))
    return feature_importance

from flask import Flask, jsonify, request, Response
from flask_cors import CORS
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    user_id = data["userId"]
    name = data["password"]
    print(user_id)
    print(name)
    df = pd.DataFrame.from_records((col.find({"Customer_ID":int(user_id)}, {"_id":0})))
    print(df)
    if df.shape[0]>0 and (df["Name"].values[0].split(" ")[0].lower()==name.lower()):
        return jsonify({"message": "Login Successfull"})
    else:
        return Response(jsonify({"message": "Login Failed"}),status=403)

@app.route("/credit_score/<user_id>", methods=["GET"])
def get_credit_score(user_id):
    pred , allowed_credit_limit, user_profile_ip = get_user_profile(user_id)
    response = get_credit_score_expl(user_profile_ip, pred, allowed_credit_limit, get_model_feature_imps())
    print(response)
    response = response.strip()
    return jsonify({"userProfile": response, "userCreditProfile": pred, "allowedCreditLimit": allowed_credit_limit, "userId": user_id})

@app.route("/product_suggestions", methods=["POST"])
def product_suggetions():
    data = request.get_json()
    user_profile = data["userProfile"]
    user_id = data["userId"]
    pred = data["userCreditProfile"]
    allowed_credit_limit = data["allowedCreditLimit"]
    _,_,user_profile_ip = get_user_profile(user_id)
    user_profile_ip_final = {}
    # Select only specific fields required in for retrieving relevant products
    for k in ["Occupation", "Annual_Income", "Monthly_Inhand_Salary", "Type_of_Loan", "Credit_Mix", "Payment_of_Min_Amount", "Total_EMI_per_month", "Amount_invested_monthly", "Payment_Behaviour"]:
        user_profile_ip_final[k] = user_profile_ip[k]
    card_suggestions = get_product_suggestions(user_profile, json.dumps(user_profile_ip_final), pred, allowed_credit_limit)
    product_recommendations = get_credit_card_recommendations(user_profile, json.dumps(user_profile_ip_final), pred, \
                                                              allowed_credit_limit, card_suggestions)
    product_recommendations = product_recommendations.replace("\n","").replace('\"', '"').strip()
    print(product_recommendations)
    return jsonify({"productRecommendations": json.loads(product_recommendations)})

if __name__ == "__main__":   # Please do not set debug=True in production
    # print(get_user_profile(8625))
    app.run(host="0.0.0.0", port=5000, debug=True)