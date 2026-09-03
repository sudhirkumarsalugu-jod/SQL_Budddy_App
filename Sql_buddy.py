#--------------------------------------
#    IMPORT SECION 
#--------------------------------------
import mysql.connector
from openai import OpenAI
import pandas as pd
import os 
import streamlit as st 
from dotenv import load_dotenv

load_dotenv()

#-------------
#   Page setup

st.title("SQL BUDDY")


#setting up nvidia client and api



#setting up mysql:
def connect_to_mysql():
    conn = mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = "Encrypted@405",
        database = "school_db"
    )
    return conn

    if conn:
        print("Connected Sucessfully")
    else:
        print("Connection Failed")


csv = st.file_uploader("Upload Your Table Schema", type=["csv"])

API_KEY = os.getenv("Nvedia_Api_Key")

if API_KEY is None:
    API_KEY = st.secrets["Nvedia_Api_Key"]
    st.markdown("API KEY LOADED ✅")
else:
    st.markdown("API KEY LOADED ✅")

client = OpenAI(
api_key=API_KEY,
base_url="https://integrate.api.nvidia.com/v1")

schema = None

if csv is not None:
    st.markdown("File Uploaded✅")
    schema = pd.read_csv(csv, encoding="utf 8")


#creating sql query 
def generate_query(natural_language_query):
    prompt = f"Given the following database schema: {schema} Convert this question into a SQL query. Only return the SQL query without any explanation: {natural_language_query}"
    return prompt

#calling nvidia ai 

user_propmt = st.text_input("Ask your Query In Simple Language: ")

if st.button("Get Query"):
    prompt = generate_query(user_propmt)

    response = client.chat.completions.create(
        model="nvidia/nemotron-3-super-120b-a12b",
        messages=[
            {
                "role": "user",
                "content": prompt}
        ]
    )

    st.markdown(response.choices[0].message.content)

#saving the ai input 
    sql_prompt = response.choices[0].message.content
    print(sql_prompt)

#connecting to my sql
    conn = connect_to_mysql()
    cursor = conn.cursor()
    cursor.execute(sql_prompt)
    results = cursor.fetchall()

#printing results
    for row in results:
        print(row)

    cursor.close()
    conn.close()


