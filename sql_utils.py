import re

# Statements that change data or the database. SQL Buddy only runs read-only queries.
BLOCKED_WORDS = ("insert", "update", "delete", "drop", "alter", "truncate",
                 "create", "replace", "grant", "revoke", "rename")


def clean_sql(text):
    """Remove markdown code fences and extra spaces from the model's reply."""
    text = (text or "").strip()
    text = re.sub(r"^```(?:sql)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def is_safe_select(sql):
    """Return True only for a single read-only SELECT (or WITH ... SELECT) query."""
    sql = clean_sql(sql).rstrip(";").strip()
    if not sql or ";" in sql:                      # empty, or more than one statement
        return False
    if not re.match(r"^(select|with)\b", sql, flags=re.IGNORECASE):
        return False
    pattern = r"\b(" + "|".join(BLOCKED_WORDS) + r")\b"
    return re.search(pattern, sql, flags=re.IGNORECASE) is None
