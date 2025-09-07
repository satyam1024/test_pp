import openai
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential
from ..core.config import OPENAI_API_KEY
from .prompt_builder import build_prompt

openai.api_key = OPENAI_API_KEY

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2))
def generate_sql(question: str) -> str:
    prompt = build_prompt(question)
    logger.debug(f"LLM prompt:\n{prompt}")

    resp = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )

    sql = resp["choices"][0]["message"]["content"].strip()
    logger.info(f"Generated SQL: {sql}")
    return sql
