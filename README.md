# SQL Buddy

A small Streamlit app that turns a **plain-English question into a MySQL query**, shows the generated SQL, and runs it on your database so you can see the result in a table.

Upload your table schema as a CSV, ask a question such as *"Which students scored above 80 in maths?"*, and SQL Buddy writes the query with the Google Gemini API.

## How it works

```
Schema CSV + question
   → Google Gemini API writes a MySQL SELECT query
   → the query is cleaned and checked (read-only SELECT only)
   → mysql-connector runs it on your MySQL database
   → the result is shown as a table in Streamlit
```

## Features

- Upload a table schema CSV so the model knows your table and column names
- Ask questions in simple language
- See the generated SQL before looking at the result
- **Read-only safety check:** only a single `SELECT` (or `WITH ... SELECT`) query is run. Anything that inserts, updates, deletes, drops or alters is blocked and not sent to the database
- Results are shown in an interactive table, and MySQL errors are shown as readable messages
- Database login and API key are read from environment variables, never from the code

## Tech stack

Python · Streamlit · MySQL (`mysql-connector-python`) · Google Gemini API (`google-genai`) · pandas · python-dotenv

## Project files

| File | Purpose |
|---|---|
| `Sql_buddy.py` | The Streamlit app |
| `sql_utils.py` | Helper functions that clean the model's reply and check that a query is read-only |
| `requirements.txt` | Python packages |
| `.env.example_file.txt` | Template for the settings you need in your own `.env` file |

## Setup

1. **Install the packages**
   ```bash
   pip install -r requirements.txt
   ```
2. **Create a `.env` file** in the project folder (copy the template and fill it in). This file is listed in `.gitignore`, so it is never committed.
   ```
   GOOGLE_API_KEY=your_gemini_api_key_here
   DB_Password=your_mysql_password_here
   DB_HOST=localhost
   DB_USER=root
   DB_NAME=school_db
   ```
3. **Make sure MySQL is running** and the database named in `DB_NAME` exists.
4. **Start the app**
   ```bash
   streamlit run Sql_buddy.py
   ```

## How to use it

1. Upload a CSV that describes your tables (for example, columns such as `table_name`, `column_name`, `data_type`).
2. Type your question in the box.
3. Click **Get Query**. The generated SQL appears first, then the result table.

## Safety notes

- The safety check is a basic guard: it allows one `SELECT` statement and blocks data-changing keywords. It is **not a substitute for database permissions**. For anything beyond local practice, connect with a MySQL user that only has `SELECT` rights.
- The model's SQL can be wrong, so always read the generated query before trusting the result.
- Your schema CSV is sent to the Gemini API as part of the prompt, so do not upload schemas that contain confidential information.

## Limitations and ideas for next steps

- Works with one schema CSV at a time, and does not read the schema directly from MySQL yet
- No query history or saved questions
- Could add a button to download the result as CSV, and a "retry" when the generated query fails

## Author

**Sudhir Kumar Salugu** — [LinkedIn](https://www.linkedin.com/in/salugu-sudhir-kumar/) · [GitHub](https://github.com/sudhirkumarsalugu-jod)
