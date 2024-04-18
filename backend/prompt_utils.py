from langchain_core.prompts import PromptTemplate


get_credit_score_expl_prompt = PromptTemplate.from_template(
    """    
    ##Instruction: 
    - Take into account the Definitions of various feature field and their respective values given as input to AI/ML model that is used to predict a persons Credit Score Health.
    - Provide a detailed reason in layman language as to why a Credit request was rejected or processed given the profile of the candidate.

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
         

    Explain the Descision for Credit Score Profile and Processed Credit limit within 250 words in points:[Reason]
    """
)

get_credit_card_recommendations_prompt = PromptTemplate.from_template(
    """
    ##Instruction:
    - Given the user profile and recommended credit cards that will best fit the user profile.
    - Reason as to why the credit card is suggested to the user for each card.
    - Provide product features to help user choose

    ## User profile:
    {user_profile}

    ## Credit cards Recommendations:
    {card_suggestions}

    ## Recommendations=Output as Json with card name as Key and concise summary of card to upsell as Value:
    {{"CardName1":"personalized_product_description_1","CardName2":"personalized_product_description_2",...}}
    """
)


user_profile_based_cc_rec_prompt = PromptTemplate.from_template(
"""
## ML Model Inference Results on User Profile:
- Credit Health={pred}
- Processed Credit Limit for the user={allowed_credit_limit}

## User profile:
{user_profile}

##Values for given user profile used to predict the Credit Score Profile:
{user_profile_ip}

##Instruction: Given the user profile recommended credit cards that will best fit the user profile.
- Take into account user annual income, occupation, credit mix while preparing search term to query the vector search
-{search_term_suggestion}

"""
)
