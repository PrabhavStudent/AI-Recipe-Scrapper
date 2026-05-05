import re


INGREDIENT_PATTERN = re.compile(
    r"(?P<quantity>\d+(?:/\d+)?(?:\.\d+)?|\d+\s+\d+/\d+)?\s*"
    r"(?P<unit>cups?|tbsp|tablespoons?|tsp|teaspoons?|grams?|g|kg|ml|l|oz|ounces?|pounds?|lb|cloves?|pinch|can)?\s*"
    r"(?P<item>[A-Za-z][A-Za-z\s,\-()]+)",
    flags=re.IGNORECASE,
)


def _extract_time(text: str, label: str) -> str:
    match = re.search(rf"{label}\s*(?:time)?\s*[:\-]?\s*([\w\s]+?)(?:\n|$)", text, re.IGNORECASE)
    return match.group(1).strip() if match else "Not specified"


def _extract_title(page_title: str | None, text: str) -> str:
    if page_title:
        return page_title.split("|")[0].strip()[:120]
    first_line = next((line.strip() for line in text.splitlines() if len(line.strip()) > 4), "Untitled Recipe")
    return first_line[:120]


def fallback_generate(page_title: str | None, text: str) -> dict:
    title = _extract_title(page_title, text)
    lines = [line.strip(" -•\t") for line in text.splitlines() if line.strip()]
    ingredients = []
    instructions = []

    for line in lines:
        lower = line.lower()
        if any(word in lower for word in ["add ", "mix ", "cook ", "bake ", "stir ", "serve ", "heat ", "combine "]):
            instructions.append(line)
        elif len(ingredients) < 16:
            match = INGREDIENT_PATTERN.match(line)
            if match and match.group("item"):
                ingredients.append(
                    {
                        "quantity": match.group("quantity") or "",
                        "unit": match.group("unit") or "",
                        "item": match.group("item").strip(" ,"),
                    }
                )

    if not ingredients:
        ingredients = [
            {"quantity": "1", "unit": "serving", "item": "main ingredients from source page"},
            {"quantity": "", "unit": "", "item": "seasoning to taste"},
        ]

    if not instructions:
        instructions = [
            "Prepare all ingredients from the source recipe.",
            "Cook according to the method described on the page.",
            "Serve warm and adjust seasoning to taste.",
        ]

    recipe = {
        "title": title,
        "cuisine_type": "General",
        "prep_time": _extract_time(text, "prep"),
        "cook_time": _extract_time(text, "cook"),
        "total_time": _extract_time(text, "total"),
        "servings": "4",
        "ingredients": ingredients[:20],
        "instructions": instructions[:12],
        "difficulty": "medium" if len(instructions) > 6 else "easy",
    }

    nutrition = {
        "calories_per_serving": 420,
        "protein_g": 18,
        "carbs_g": 46,
        "fat_g": 18,
        "note": "Approximate fallback estimate. Use LLM mode for richer estimates.",
    }

    substitutions = [
        {"original": "butter", "substitute": "olive oil", "reason": "dairy-free option"},
        {"original": "cream", "substitute": "coconut milk", "reason": "lactose-free option"},
        {"original": "white rice", "substitute": "brown rice", "reason": "higher-fiber option"},
    ]

    shopping_list = {
        "produce": [item["item"] for item in ingredients if any(word in item["item"].lower() for word in ["onion", "tomato", "garlic", "pepper", "lemon"])],
        "pantry": [item["item"] for item in ingredients],
        "dairy": [],
        "protein": [item["item"] for item in ingredients if any(word in item["item"].lower() for word in ["chicken", "egg", "fish", "paneer", "tofu", "beans"])],
        "spices": ["salt", "black pepper"],
    }

    return {
        "recipe": recipe,
        "nutrition": nutrition,
        "substitutions": substitutions,
        "shopping_list": shopping_list,
        "related_recipes": [
            f"Fresh salad with {title}",
            f"Simple soup to pair with {title}",
            f"Light dessert after {title}",
        ],
    }
