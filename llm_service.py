import json
from pathlib import Path

from app.config import settings
from app.fallback_parser import fallback_generate


PROMPT_DIR = Path(__file__).resolve().parents[2] / "prompts"


def _load_prompt(name: str) -> str:
    return (PROMPT_DIR / name).read_text(encoding="utf-8")


def _json_from_text(text: str) -> dict:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("LLM response did not contain a JSON object")
    return json.loads(text[start : end + 1])


def generate_recipe_data(page_title: str | None, scraped_text: str) -> dict:
    if not settings.gemini_api_key:
        return fallback_generate(page_title, scraped_text)

    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_core.prompts import ChatPromptTemplate

    prompt = ChatPromptTemplate.from_template(_load_prompt("recipe_extraction_prompt.txt"))
    llm = ChatGoogleGenerativeAI(
        model=settings.llm_model,
        google_api_key=settings.gemini_api_key,
        temperature=0.2,
    )
    chain = prompt | llm
    response = chain.invoke({"page_title": page_title or "", "scraped_text": scraped_text})
    return _json_from_text(response.content)


def merge_shopping_lists(recipe_payloads: list[dict]) -> dict[str, list[str]]:
    merged: dict[str, list[str]] = {}

    for payload in recipe_payloads:
        shopping_list = payload.get("shopping_list", {})
        for category, items in shopping_list.items():
            merged.setdefault(category, [])
            for item in items:
                if item not in merged[category]:
                    merged[category].append(item)

    return dict(sorted(merged.items()))
