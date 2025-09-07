import re
from difflib import SequenceMatcher
from loguru import logger
from ..db.schema_loader import load_schema_from_file

MAX_TABLES = 10  

def normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (text or "").lower()).strip()

def keyword_match_score(query: str, candidate: str) -> float:
    return SequenceMatcher(None, query, candidate).ratio()

def search_relevant_tables(user_question: str, top_k: int = MAX_TABLES):
    schema = load_schema_from_file()
    question_norm = normalize(user_question)

    scores = {}
    for table, meta in schema.items():
        table_norm = normalize(table)
        table_remark = normalize(meta.get("remarks", ""))

        score = max(
            keyword_match_score(question_norm, table_norm),
            keyword_match_score(question_norm, table_remark),
        )

        for col, col_meta in meta.get("columns", {}).items():
            col_norm = normalize(col)
            col_remark = normalize(col_meta.get("remarks", ""))
            score = max(
                score,
                keyword_match_score(question_norm, col_norm),
                keyword_match_score(question_norm, col_remark),
            )

        if score > 0.1:
            scores[table] = score

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    selected = [t for t, _ in ranked[:top_k]]

    logger.info(f"Schema search for '{user_question}' → {selected}")
    return selected, ranked
