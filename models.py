from datetime import datetime

from sqlalchemy import DateTime, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class RecipeRecord(Base):
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    source_url: Mapped[str] = mapped_column(Text, nullable=False)
    page_title: Mapped[str | None] = mapped_column(Text)
    scraped_text: Mapped[str] = mapped_column(Text, nullable=False)
    recipe_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    nutrition_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    substitutions_data: Mapped[list] = mapped_column(JSON, nullable=False)
    shopping_list_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    related_recipes_data: Mapped[list] = mapped_column(JSON, nullable=False)
    difficulty: Mapped[str] = mapped_column(String(20), nullable=False)
    cuisine: Mapped[str] = mapped_column(String(80), nullable=False)
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    extracted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
