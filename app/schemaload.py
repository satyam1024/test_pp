import json
import ibm_db
from loguru import logger
from ..core.config import DB2_DSN, SCHEMA_FILE

def extract_schema():
    """Extract schema from DB2 system catalogs and save as schema.json."""
    conn = ibm_db.connect(DB2_DSN, "", "")
    query = """
        SELECT t.TABNAME, t.REMARKS, c.COLNAME, c.TYPENAME, c.REMARKS
        FROM SYSCAT.TABLES t
        JOIN SYSCAT.COLUMNS c ON t.TABNAME = c.TABNAME
        WHERE t.TYPE='T'
    """
    stmt = ibm_db.exec_immediate(conn, query)

    schema = {}
    row = ibm_db.fetch_assoc(stmt)
    while row:
        table = row["TABNAME"]
        if table not in schema:
            schema[table] = {"remarks": row.get("REMARKS", ""), "columns": {}}
        schema[table]["columns"][row["COLNAME"]] = {
            "type": row["TYPENAME"],
            "remarks": row.get("REMARKS", ""),
        }
        row = ibm_db.fetch_assoc(stmt)

    with open(SCHEMA_FILE, "w") as f:
        json.dump(schema, f, indent=2)
    logger.info(f"Schema extracted to {SCHEMA_FILE}")
    return schema


def load_schema_from_file():
    """Load schema.json."""
    with open(SCHEMA_FILE, "r") as f:
        return json.load(f)
