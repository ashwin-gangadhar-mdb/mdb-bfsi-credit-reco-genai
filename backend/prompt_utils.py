from langchain_core.prompts import PromptTemplate
from typing import List

from langchain.output_parsers import PydanticOutputParser, OutputFixingParser
# from langchain_core.pydantic_v1 import BaseModel, Field, validator
from pydantic import BaseModel, Field, validator
import os
from dotenv import load_dotenv

# from langchain_fireworks import Fireworks 

# load_dotenv()

# llm = Fireworks(
#     fireworks_api_key=os.environ["FIREWORKS_API_KEY"],
#     model="accounts/fireworks/models/mixtral-8x22b-instruct",
#     base_url="https://api.fireworks.ai/inference/v1/completions",
#     max_tokens=1024,
#     temperature=0,
#     top_p=1,
#     top_k=40
# )


get_credit_score_expl_prompt = PromptTemplate.from_template(
    """    
    You are Credit Health AI Assistant. Your task is to explain the Credit Health of a person based on the given profile.
    ##Instruction: 
    - Take into account the Definitions of various feature field and their respective values given as input to AI/ML model that is used to predict a persons Credit Score Health.
    - Provide a detailed reason in layman language as to why a Credit request was rejected or processed given the profile of the candidate.
    - Avoid mentioning model defintions or feature importances score from the model.

    ##Definitions:
    Month: Represents the month of the year
    Name: Represents the name of a human
    Age: Represents the age of the human
    Occupation: Represents the occupation of the human
    Annual_Income: Represents the annual income of the human
    Monthly_Inhand_Salary: Represents the monthly base salary of a human
    Num_Bank_Accounts: Represents the number of bank accounts a human holds
    Num_Credit_Card: Represents the number of other credit cards held by a human
    Interest_Rate: Represents the interest rate on credit card
    Num_of_Loan: Represents the number of loans taken from the bank
    Type_of_Loan: Represents the types of loan taken by a human
    Delay_from_due_date: Represents the average number of days delayed from the payment date
    Num_of_Delayed_Payment: Represents the average number of payments delayed by a human
    Changed_Credit_Limit: Represents the percentage change in credit card limit
    Num_Credit_Inquiries: Represents the number of credit card inquiries
    Credit_Mix: Represents the classification of the mix of credits
    Outstanding_Debt: Represents the remaining debt to be paid (in USD)
    Credit_Utilization_Ratio: Represents the utilization ratio of credit card
    Credit_History_Age: Represents the age of credit history of the human
    Payment_of_Min_Amount: Represents whether only the minimum amount was paid by the human
    Total_EMI_per_month: Represents the monthly EMI payments (in USD)
    Amount_invested_monthly: Represents the monthly amount invested by the customer (in USD)
    Payment_Behaviour: Represents the payment behavior of the customer
    Monthly_Balance: Represents the monthly balance amount of the customer (in USD)

    ##Feature importace of the model used:
    {feature_importance}

    ##Values for given profile to be use to predict the Result(Credit Score Profile) with a reason:
    {user_profile_ip}

    ## Model Inference Results:
    - Credit Health={pred}
    - Processed Credit Limit for the user={allowed_credit_limit}
         

    Explain the Descision in detail for Credit Health and Processed Credit limit within 250 words:[Reason]
    """
)


class CreditCard(BaseModel):
    name: str = Field(description="name of an credit card")
    description: str = Field(description="Presonlized description of the credit card in 50 words")

class Recommendations(BaseModel):
    card_suggestions: List[CreditCard] = Field(description="List of credit card recommendations")

recommendation_parser = PydanticOutputParser(pydantic_object=Recommendations)
# new_parser = OutputFixingParser.from_llm(parser=recommendation_parser, llm=llm)

get_credit_card_recommendations_prompt = PromptTemplate(
    template="""
    You are are a Credit Card recommendation AI assistant. Your task is to generate different credit card names and product summaries for the given user profile.
    ##Instruction:
    - Given the user profile and recommended credit cards that will best fit the user profile.
    - Reason as to why the credit card is suggested to the user for each card.
    - Provide product features to help user choose

    ## User profile:
    {user_profile}

    ## Credit cards Recommendations:
    {card_suggestions}

    Output in Json format example below
    ```json
    
    ````

    ## Format Instructions: {format_instruction}

    """,
    input_variables=["user_profile", "card_suggestions"],
    partial_variables={"format_instruction": recommendation_parser.get_format_instructions()}
)

    # ## Recommendations=Output as Json with card name as Key and concise summary of the card as value:
    # Output:{{"CardName1":"personalized_product_description_1","CardName2":"personalized_product_description_2",...}}


user_profile_based_cc_rec_prompt = PromptTemplate(
    template="""
    You are an AI assistant. Your task is to generate different credit card names and product summaries for the given user profile.
    - By generating multiple perspectives on the user profile and instruction, your goal is to help

    ## ML Model Inference Results on User Profile:
    - Credit Health={pred}
    - Processed Credit Limit for the user={allowed_credit_limit}

    User profile={user_profile}
    Occupation={occupation}
    Annual Incode={annual_income}
    Monthly Inhand Salary={monthly_inhand_salary}

    ##Instruction: Given the user profile recommended credit cards suggestion that will best fit the user profile as per format instructions given below .
    - Take into account user annual income, occupation, montly inhand salary while preparing search term to query the vector search
    -{search_term_suggestion}

    Output in Json format example below
    ```json

    ````
    
    ## Result Format Instructions:{format_instruction}
    

    """,
    input_variables=['user_profile', 'pred', 'allowed_credit_limit', 'search_term_suggestion', 'occupation', 'annual_income', 'monthly_inhand_salary'],
    partial_variables={"format_instruction": recommendation_parser.get_format_instructions()}
)

