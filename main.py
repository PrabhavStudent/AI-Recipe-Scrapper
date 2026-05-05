from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.config import settings
from app.database import Base, engine, get_db
from app.llm_service import generate_recipe_data, merge_shopping_lists
from app.models import RecipeRecord
from app.schemas import ExtractRecipeRequest, MealPlanRequest, MealPlanResponse, RecipeHistoryItem, RecipeResponse
from app.scraper import scrape_page


Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Recipe Scraper API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://127.0.0.1:5500", "http://127.0.0.1:5501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def to_response(record: RecipeRecord) -> RecipeResponse:
    return RecipeResponse(
        id=record.id,
        source_url=record.source_url,
        page_title=record.page_title,
        recipe=record.recipe_data,
        nutrition=record.nutrition_data,
        substitutions=record.substitutions_data,
        shopping_list=record.shopping_list_data,
        related_recipes=record.related_recipes_data,
        scraped_text_preview=record.scraped_text[:1000],
        extracted_at=record.extracted_at,
    )


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "AI Recipe Scraper API is running"}


@app.post("/api/recipes/extract", response_model=RecipeResponse)
def extract_recipe(payload: ExtractRecipeRequest, db: Session = Depends(get_db)) -> RecipeResponse:
    try:
        scraped = scrape_page(str(payload.url))
        generated = generate_recipe_data(scraped["page_title"], scraped["text"])
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not extract recipe: {exc}") from exc

    recipe = generated["recipe"]
    record = RecipeRecord(
        source_url=str(payload.url),
        page_title=scraped["page_title"],
        scraped_text=scraped["text"],
        recipe_data=recipe,
        nutrition_data=generated["nutrition"],
        substitutions_data=generated["substitutions"],
        shopping_list_data=generated["shopping_list"],
        related_recipes_data=generated["related_recipes"],
        title=recipe.get("title", "Untitled Recipe"),
        cuisine=recipe.get("cuisine_type", "General"),
        difficulty=recipe.get("difficulty", "medium"),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return to_response(record)


@app.get("/api/recipes", response_model=list[RecipeHistoryItem])
def list_recipes(db: Session = Depends(get_db)) -> list[RecipeHistoryItem]:
    return db.query(RecipeRecord).order_by(RecipeRecord.extracted_at.desc()).all()


@app.get("/api/recipes/{recipe_id}", response_model=RecipeResponse)
def get_recipe(recipe_id: int, db: Session = Depends(get_db)) -> RecipeResponse:
    record = db.get(RecipeRecord, recipe_id)
    if not record:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return to_response(record)


@app.post("/api/meal-planner", response_model=MealPlanResponse)
def meal_planner(payload: MealPlanRequest, db: Session = Depends(get_db)) -> MealPlanResponse:
    records = db.query(RecipeRecord).filter(RecipeRecord.id.in_(payload.recipe_ids)).all()
    if len(records) != len(set(payload.recipe_ids)):
        raise HTTPException(status_code=404, detail="One or more recipes were not found")

    recipe_payloads = [
        {
            "title": record.title,
            "shopping_list": record.shopping_list_data,
        }
        for record in records
    ]
    return MealPlanResponse(
        recipe_ids=payload.recipe_ids,
        recipe_titles=[record.title for record in records],
        combined_shopping_list=merge_shopping_lists(recipe_payloads),
    
