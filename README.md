# AI Recipe Scraper

AI Recipe Scraper is a full-stack recipe extraction project. It scrapes recipe blog HTML with BeautifulSoup, sends cleaned text to an LLM through LangChain/Gemini, stores structured and generated recipe data in a local SQLite database by default, and displays the results in a clean React UI.

The app includes a fallback parser so the project can still demo without a Gemini API key. With `GEMINI_API_KEY` configured, the backend uses LangChain and Gemini.

## Features

- Scrape recipe blog URLs with BeautifulSoup
- Extract structured recipe data:
  - title
  - cuisine type
  - prep time, cook time, total time
  - servings
  - ingredients with quantity, unit, and item
  - step-by-step instructions
  - difficulty level
- Generate nutrition estimate per serving
- Generate 3 ingredient substitutions
- Generate shopping list grouped by category
- Suggest 3 related recipes
- Store scraped and generated data in SQLite locally, with optional MySQL support
- React frontend:
  - Tab 1: URL input and structured recipe result
  - Tab 2: historical recipe table
  - reusable details modal
  - optional meal planner mode for 3 to 5 saved recipes

## Project Structure

```text
recipe-ai-scraper/
  backend/
    app/
      config.py
      database.py
      fallback_parser.py
      llm_service.py
      main.py
      models.py
      schemas.py
      scraper.py
    .env.example
    requirements.txt
  frontend/
    src/
      main.jsx
      styles.css
    index.html
    package.json
  prompts/
    recipe_extraction_prompt.txt
    nutrition_prompt.txt
    substitution_prompt.txt
    meal_planner_prompt.txt
  sample_data/
    example_recipe_urls.txt
    api_outputs/
      lasagna_output.json
    screenshots/
      README.md
  docker-compose.yml
  README.md
```

## Prerequisites

- Python 3.11 or newer
- Node.js 18 or newer
- Docker Desktop or local MySQL
- Optional Gemini API key from Google AI Studio

## Database Setup

For the easiest local run, no database setup is needed. The backend uses this local SQLite file by default:

```text
backend/recipe_ai.db
```

The active `.env` value is:

```text
DATABASE_URL=sqlite:///./recipe_ai.db
```

### Optional MySQL

Using Docker:

```bash
cd /mnt/c/Users/ussha/recipe-ai-scraper
docker compose up -d
```

This starts MySQL at:

```text
localhost:3306
```

Database credentials:

```text
database: recipe_ai
user: root
password: root
```

If you are using local MySQL instead of Docker, create the database manually:

```bash
sudo apt update
sudo apt install mysql-server
sudo service mysql start
```

Then open MySQL:

```bash
sudo mysql
```

Then run:

```sql
CREATE DATABASE recipe_ai CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'root';
FLUSH PRIVILEGES;
EXIT;
```

Your backend `.env` should contain:

```text
DATABASE_URL=mysql+pymysql://root:root@localhost:3306/recipe_ai
```

## Setup Backend

```bash
cd /mnt/c/Users/ussha/recipe-ai-scraper/backend
cp .env.example .env
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Optional: edit `.env` and add Gemini:

```text
GEMINI_API_KEY=your_key_here
LLM_MODEL=gemini-1.5-flash
```

Start backend:

```bash
uvicorn app.main:app --reload
```

Backend URL:

```text
http://127.0.0.1:8000
```

API docs:

```text
http://127.0.0.1:8000/docs
```

## Setup Frontend

```bash
cd /mnt/c/Users/ussha/recipe-ai-scraper/frontend
npm install
npm run dev
```

If you are running from WSL inside `/mnt/c` and npm fails with `EPERM chmod`, use:

```bash
npm install --no-bin-links
node node_modules/vite/bin/vite.js --host 127.0.0.1
```

Frontend URL:

```text
http://127.0.0.1:5173
```

## API Endpoints

### Health Check

```http
GET /
```

### Extract Recipe

```http
POST /api/recipes/extract
Content-Type: application/json

{
  "url": "https://www.allrecipes.com/recipe/24074/alysias-basic-meat-lasagna/"
}
```

Returns:

- scraped text preview
- structured recipe
- nutrition estimate
- substitutions
- shopping list
- related recipes
- database id
- extraction date

### Recipe History

```http
GET /api/recipes
```

Returns:

```json
[
  {
    "id": 1,
    "title": "Alysia's Basic Meat Lasagna",
    "cuisine": "Italian-American",
    "difficulty": "medium",
    "extracted_at": "2026-05-05T10:00:00Z"
  }
]
```

### Recipe Details

```http
GET /api/recipes/1
```

### Meal Planner

```http
POST /api/meal-planner
Content-Type: application/json

{
  "recipe_ids": [1, 2, 3]
}
```

Returns a merged shopping list grouped by category.

## Testing Steps

1. Start MySQL with `docker compose up -d` or start your local MySQL service.
2. Start backend with `uvicorn app.main:app --reload`.
3. Start frontend with `npm run dev`.
4. Open `http://127.0.0.1:5173`.
5. Paste a recipe blog URL.
6. Click `Extract Recipe`.
7. Confirm structured recipe cards appear in Tab 1.
8. Open Tab 2 and confirm the recipe is saved in history.
9. Click `Open` to view the details modal.
10. Extract at least 3 recipes, select them in Tab 2, and click `Merge Shopping List`.

## Sample Data

Recipe URLs tested are stored in:

```text
sample_data/example_recipe_urls.txt
```

Example JSON output is stored in:

```text
sample_data/api_outputs/lasagna_output.json
```

Screenshot checklist is stored in:

```text
sample_data/screenshots/README.md
```

## Prompt Templates

LangChain prompt templates are stored in:

```text
prompts/recipe_extraction_prompt.txt
prompts/nutrition_prompt.txt
prompts/substitution_prompt.txt
prompts/meal_planner_prompt.txt
```

The active backend chain uses `recipe_extraction_prompt.txt` to return a complete JSON object containing recipe extraction, nutrition, substitutions, shopping list, and related recipes. Separate prompt files are included for submission clarity and future chain splitting.

## Notes

- This project scrapes HTML recipe blog pages only.
- It does not use external recipe APIs.
- Nutrition values are approximate and should not be treated as medical advice.
- Some recipe sites block scraping. Use normal public recipe pages for testing.

Thank you
