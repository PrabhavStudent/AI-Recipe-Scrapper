import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import { BookOpen, CalendarPlus, ChefHat, Clock, ExternalLink, History, ListPlus, Search, X } from "lucide-react";
import "./styles.css";

const API_URL = "http://127.0.0.1:8000";

function Tag({ children }) {
  return <span className="tag">{children}</span>;
}

function InfoCard({ title, children }) {
  return (
    <section className="card">
      <h3>{title}</h3>
      {children}
    </section>
  );
}

function RecipeDetails({ data }) {
  if (!data) {
    return <div className="empty-state">Extract or select a recipe to view details.</div>;
  }

  const recipe = data.recipe;
  return (
    <div className="details-grid">
      <InfoCard title="Recipe Details">
        <div className="title-row">
          <ChefHat size={28} />
          <div>
            <h2>{recipe.title}</h2>
            <div className="tag-row">
              <Tag>{recipe.cuisine_type}</Tag>
              <Tag>{recipe.difficulty}</Tag>
              <Tag>{recipe.servings} servings</Tag>
            </div>
          </div>
        </div>
        <div className="time-grid">
          <span><Clock size={16} /> Prep: {recipe.prep_time}</span>
          <span><Clock size={16} /> Cook: {recipe.cook_time}</span>
          <span><Clock size={16} /> Total: {recipe.total_time}</span>
        </div>
      </InfoCard>

      <InfoCard title="Nutrition Estimate">
        <div className="nutrition-grid">
          <strong>{data.nutrition.calories_per_serving} kcal</strong>
          <span>Protein {data.nutrition.protein_g}g</span>
          <span>Carbs {data.nutrition.carbs_g}g</span>
          <span>Fat {data.nutrition.fat_g}g</span>
        </div>
        <p className="muted">{data.nutrition.note}</p>
      </InfoCard>

      <InfoCard title="Ingredients">
        <ul className="clean-list">
          {recipe.ingredients.map((ingredient, index) => (
            <li key={`${ingredient.item}-${index}`}>
              <strong>{[ingredient.quantity, ingredient.unit].filter(Boolean).join(" ")}</strong> {ingredient.item}
            </li>
          ))}
        </ul>
      </InfoCard>

      <InfoCard title="Instructions">
        <ol className="steps">
          {recipe.instructions.map((step, index) => (
            <li key={`${step}-${index}`}>{step}</li>
          ))}
        </ol>
      </InfoCard>

      <InfoCard title="Ingredient Substitutions">
        <div className="stack">
          {data.substitutions.map((item, index) => (
            <div className="substitution" key={`${item.original}-${index}`}>
              <strong>{item.original} → {item.substitute}</strong>
              <p>{item.reason}</p>
            </div>
          ))}
        </div>
      </InfoCard>

      <InfoCard title="Shopping List">
        <ShoppingList list={data.shopping_list} />
      </InfoCard>

      <InfoCard title="Related Recipes">
        <ul className="clean-list">
          {data.related_recipes.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </InfoCard>
    </div>
  );
}

function ShoppingList({ list }) {
  return (
    <div className="shopping-grid">
      {Object.entries(list || {}).map(([category, items]) => (
        <div className="shopping-category" key={category}>
          <h4>{category}</h4>
          <ul>
            {(items || []).map((item) => <li key={item}>{item}</li>)}
          </ul>
        </div>
      ))}
    </div>
  );
}

function DetailsModal({ recipe, onClose }) {
  if (!recipe) return null;

  return (
    <div className="modal-backdrop" role="presentation" onClick={onClose}>
      <div className="modal" role="dialog" aria-modal="true" onClick={(event) => event.stopPropagation()}>
        <button className="icon-button close" onClick={onClose} aria-label="Close details">
          <X size={20} />
        </button>
        <RecipeDetails data={recipe} />
      </div>
    </div>
  );
}

function ExtractTab({ currentRecipe, setCurrentRecipe, refreshHistory }) {
  const [url, setUrl] = useState("https://www.allrecipes.com/recipe/24074/alysias-basic-meat-lasagna/");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function extractRecipe(event) {
    event.preventDefault();
    setLoading(true);
    setError("");

    try {
      const response = await fetch(`${API_URL}/api/recipes/extract`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });

      if (!response.ok) {
        const payload = await response.json();
        throw new Error(payload.detail || "Extraction failed");
      }

      const data = await response.json();
      setCurrentRecipe(data);
      refreshHistory();
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="tab-layout">
      <form className="url-panel" onSubmit={extractRecipe}>
        <div>
          <label htmlFor="recipe-url">Recipe blog URL</label>
          <div className="url-row">
            <input
              id="recipe-url"
              type="url"
              value={url}
              onChange={(event) => setUrl(event.target.value)}
              placeholder="https://example.com/recipe"
              required
            />
            <button type="submit" disabled={loading}>
              <Search size={18} />
              {loading ? "Extracting..." : "Extract Recipe"}
            </button>
          </div>
        </div>
        {error && <p className="error">{error}</p>}
      </form>
      <RecipeDetails data={currentRecipe} />
    </div>
  );
}

function HistoryTab({ history, setHistory, setModalRecipe }) {
  const [selected, setSelected] = useState([]);
  const [mealPlan, setMealPlan] = useState(null);
  const [error, setError] = useState("");

  function toggleRecipe(id) {
    setSelected((items) => (items.includes(id) ? items.filter((item) => item !== id) : [...items, id].slice(0, 5)));
  }

  async function openDetails(id) {
    const response = await fetch(`${API_URL}/api/recipes/${id}`);
    setModalRecipe(await response.json());
  }

  async function generateMealPlan() {
    setError("");
    setMealPlan(null);

    if (selected.length < 3) {
      setError("Select 3 to 5 recipes for meal planner mode.");
      return;
    }

    const response = await fetch(`${API_URL}/api/meal-planner`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ recipe_ids: selected }),
    });

    if (!response.ok) {
      setError("Could not create meal plan.");
      return;
    }

    setMealPlan(await response.json());
  }

  return (
    <div className="history-layout">
      <section className="card">
        <div className="section-title">
          <h3>Historical Recipes</h3>
          <button type="button" onClick={() => setHistory([])}>Clear View</button>
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Plan</th>
                <th>Title</th>
                <th>Cuisine</th>
                <th>Difficulty</th>
                <th>Date Extracted</th>
                <th>Details</th>
              </tr>
            </thead>
            <tbody>
              {history.map((item) => (
                <tr key={item.id}>
                  <td><input type="checkbox" checked={selected.includes(item.id)} onChange={() => toggleRecipe(item.id)} /></td>
                  <td>{item.title}</td>
                  <td>{item.cuisine}</td>
                  <td><Tag>{item.difficulty}</Tag></td>
                  <td>{new Date(item.extracted_at).toLocaleString()}</td>
                  <td>
                    <button type="button" onClick={() => openDetails(item.id)}>
                      <BookOpen size={16} />
                      Open
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="card">
        <div className="section-title">
          <h3>Meal Planner</h3>
          <button type="button" onClick={generateMealPlan}>
            <ListPlus size={16} />
            Merge Shopping List
          </button>
        </div>
        <p className="muted">Select 3 to 5 saved recipes from the table.</p>
        {error && <p className="error">{error}</p>}
        {mealPlan && (
          <>
            <div className="tag-row">{mealPlan.recipe_titles.map((title) => <Tag key={title}>{title}</Tag>)}</div>
            <ShoppingList list={mealPlan.combined_shopping_list} />
          </>
        )}
      </section>
    </div>
  );
}

function App() {
  const [activeTab, setActiveTab] = useState("extract");
  const [currentRecipe, setCurrentRecipe] = useState(null);
  const [history, setHistory] = useState([]);
  const [modalRecipe, setModalRecipe] = useState(null);

  async function refreshHistory() {
    try {
      const response = await fetch(`${API_URL}/api/recipes`);
      setHistory(await response.json());
    } catch {
      setHistory([]);
    }
  }

  useEffect(() => {
    refreshHistory();
  }, []);

  const tabContent = useMemo(() => {
    if (activeTab === "history") {
      return <HistoryTab history={history} setHistory={setHistory} setModalRecipe={setModalRecipe} />;
    }
    return <ExtractTab currentRecipe={currentRecipe} setCurrentRecipe={setCurrentRecipe} refreshHistory={refreshHistory} />;
  }, [activeTab, currentRecipe, history]);

  return (
    <main className="app-shell">
      <header className="hero">
        <div>
          <p className="eyebrow">Recipe Intelligence</p>
          <h1>AI Recipe Scraper</h1>
          <p>Scrape recipe blogs, structure ingredients and steps, estimate nutrition, generate substitutions, and save every result.</p>
        </div>
        <a href={`${API_URL}/docs`} target="_blank" rel="noreferrer">
          API Docs <ExternalLink size={16} />
        </a>
      </header>

      <nav className="tabs" aria-label="Recipe app tabs">
        <button className={activeTab === "extract" ? "active" : ""} onClick={() => setActiveTab("extract")}>
          <Search size={18} />
          Extract Recipe
        </button>
        <button className={activeTab === "history" ? "active" : ""} onClick={() => setActiveTab("history")}>
          <History size={18} />
          History
        </button>
        <button className="ghost" onClick={refreshHistory}>
          <CalendarPlus size={18} />
          Refresh
        </button>
      </nav>

      {tabContent}
      <DetailsModal recipe={modalRecipe} onClose={() => setModalRecipe(null)} />
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);
