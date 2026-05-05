from bs4 import BeautifulSoup
import requests


def scrape_page(url: str) -> dict[str, str]:
    response = requests.get(
        url,
        timeout=20,
        headers={
            "User-Agent": "Mozilla/5.0 recipe-ai-scraper student project",
            "Accept": "text/html,application/xhtml+xml",
        },
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "noscript", "svg", "iframe", "form", "nav", "footer"]):
        tag.decompose()

    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    candidates = soup.select("article, main, [class*=recipe], [id*=recipe], body")
    container = max(candidates, key=lambda node: len(node.get_text(" ", strip=True))) if candidates else soup
    text = container.get_text("\n", strip=True)
    clean_lines = [line.strip() for line in text.splitlines() if line.strip()]
    clean_text = "\n".join(clean_lines)

    return {
        "page_title": title,
        "text": clean_text[:30000],
    }
