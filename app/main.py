from fastapi import FastAPI
from pydantic import BaseModel
import ibm_db
from loguru import logger
from ..core import config
from ..llm.llm_client import generate_sql
from ..sql.validator import validate_and_fix
from ..db.schema_loader import load_schema_from_file

app = FastAPI(title="NL2SQL DB2 Prototype")

class QueryRequest(BaseModel):
    question: str

@app.post("/query")
def query_db(req: QueryRequest):
    try:
        sql = generate_sql(req.question)
        sql, warnings = validate_and_fix(sql)

        conn = ibm_db.connect(config.DB2_DSN, "", "")
        stmt = ibm_db.exec_immediate(conn, sql)

        rows = []
        result = ibm_db.fetch_assoc(stmt)
        while result:
            rows.append(result)
            result = ibm_db.fetch_assoc(stmt)

        return {"sql": sql, "rows": rows, "warnings": warnings}
    except Exception as e:
        logger.exception("Query failed")
        return {"error": str(e)}

@app.get("/schema")
def get_schema_summary():
    schema = load_schema_from_file()
    summary = {k: list(v["columns"].keys()) for k, v in list(schema.items())[:50]}
    return summary
