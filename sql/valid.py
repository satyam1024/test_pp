import sqlglot
from ..core.config import ROW_LIMIT_DEFAULT

def validate_and_fix(sql: str) -> (str, list):
    warnings = []
    try:
        parsed = sqlglot.parse_one(sql)
    except Exception as e:
        raise ValueError(f"Invalid SQL: {e}")

    if parsed.key != "select":
        raise ValueError("Only SELECT queries are allowed.")

    sql_str = sql.upper()
    if "FETCH FIRST" not in sql_str and "LIMIT" not in sql_str:
        sql += f" FETCH FIRST {ROW_LIMIT_DEFAULT} ROWS ONLY"
        warnings.append("Row limit added automatically.")

    return sql, warnings
