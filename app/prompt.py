from ..db.schema_loader import load_schema_from_file
from ..db.schema_search import search_relevant_tables
from ..core.config import ROW_LIMIT_DEFAULT

FEW_SHOT = """
User: Show all customers
SQL: SELECT * FROM CUST_TBL FETCH FIRST 100 ROWS ONLY;

User: Show total order amount per customer
SQL: SELECT C.CST_ID, SUM(O.AMT_ORD) AS TOTAL_AMOUNT
     FROM CUST_TBL C JOIN ORD_T O ON C.CST_ID = O.CST_ID
     GROUP BY C.CST_ID FETCH FIRST 100 ROWS ONLY;
"""

def build_prompt(question: str):
    schema = load_schema_from_file()
    selected, _ = search_relevant_tables(question)

    schema_context = ""
    for t in selected:
        cols = schema[t]["columns"]
        cols_str = ", ".join(
            [f"{c} ({cols[c].get('remarks', '')})" for c in cols]
        )
        schema_context += f"Table {t} ({schema[t].get('remarks','')}): {cols_str}\n"

    prompt = f"""
You are an assistant that generates DB2 SQL queries from natural language.
Only output SQL. Use FETCH FIRST {ROW_LIMIT_DEFAULT} ROWS ONLY if missing.

Schema context:
{schema_context}

Few-shot examples:
{FEW_SHOT}

User: {question}
SQL:
"""
    return prompt
