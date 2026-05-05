from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, HttpUrl


class ExtractRecipeRequest(BaseModel):
    url: HttpUrl


class MealPlanRequest(BaseModel):
    recipe_ids: list[int] = Field(..., min_length=3, max_length=5)


class RecipeHistoryItem(BaseModel):
    id: int
    title: str
    cuisine: str
    difficulty: str
    extracted_at: datetime

    model_config = {"from_attributes": True}


class RecipeResponse(BaseModel):
    id: int
    source_url: str
    page_title: str | None
    recipe: dict[str, Any]
    nutrition: dict[str, Any]
    substitutions: list[dict[str, Any]]
    shopping_list: dict[str, list[str]]
    related_recipes: list[str]
    scraped_text_preview: str
    extracted_at: datetime


class MealPlanResponse(BaseModel):
    recipe_ids: list[int]
    recipe_titles: list[str]
    combined_shopping_list: dict[str, list[str]]
