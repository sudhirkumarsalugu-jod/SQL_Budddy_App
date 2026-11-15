# SQL Buddy: ask a question in plain English, get a SQL query, and see the result.

# pyright: reportMissingModuleSource=false, reportMissingImports=false

import os
import google.genai as genai
import mysql.connector
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from sql_utils import clean_sql, is_safe_select

load_dotenv()

# ---------- Settings (all read from the environment / .env file) ----------
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_Password")
DB_NAME = os.getenv("DB_NAME", "school_db")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

st.title("SQL BUDDY")


def connect_to_mysql():
    return mysql.connector.connect(
        host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME
    )


def get_api_key():
    key = os.getenv("GOOGLE_API_KEY")
    if key:
        return key
    try:                                   # Streamlit Cloud keeps secrets here
        return st.secrets["GOOGLE_API_KEY"]
    except Exception:
        return None


API_KEY = get_api_key()
if API_KEY is None:
    st.error("GOOGLE_API_KEY not found. Add it to your .env file or Streamlit secrets.")
    st.stop()
client = genai.Client(api_key=API_KEY)

# ---------- Inputs ----------
csv = st.file_uploader("Upload Your Table Schema", type=["csv"])
schema = None
if csv is not None:
    schema = pd.read_csv(csv, encoding="utf-8")
    st.success("Schema loaded")

question = st.text_input("Ask your query in simple language:")


def build_prompt(schema_df, user_question):
    return (
        "Given the following MySQL database schema:\n"
        f"{schema_df.to_string(index=False)}\n\n"
        "Convert this question into a single MySQL SELECT query. "
        "Return only the SQL query, with no explanation:\n"
        f"{user_question}"
    )


# ---------- Run ----------
if st.button("Get Query"):
    if schema is None:
        st.warning("Please upload your table schema CSV first.")
        st.stop()
    if not question.strip():
        st.warning("Please type a question.")
        st.stop()

    response = client.models.generate_content(
        model=MODEL_NAME, contents=build_prompt(schema, question)
    )
    sql = clean_sql(response.text)
    st.subheader("Generated SQL")
    st.code(sql, language="sql")

    if not is_safe_select(sql):
        st.error("Only a single read-only SELECT query is allowed, so this was not run.")
        st.stop()

    conn = None
    try:
        conn = connect_to_mysql()
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        cursor.close()
        st.subheader("Result")
        st.dataframe(pd.DataFrame(rows, columns=columns))
    except mysql.connector.Error as err:
        st.error(f"MySQL error: {err}")
    finally:
        if conn is not None and conn.is_connected():
            conn.close()