from langchain.tools import tool
import requests, re, json

@tool
def habr_articles(query: str = "") -> str:
    """Статьи с Habr."""
    r = requests.get("https://habr.com/ru/feed/", headers={"User-Agent":"Mozilla/5.0"}, timeout=15)
    m = re.search(r'window\.__PINIA_STATE__\s*=\s*({.*?});', r.text, re.DOTALL)
    if not m: return "Ошибка"
    data = json.loads(m.group(1))
    articles = []
    for aid, a in data.get("articlesList",{}).get("articlesList",{}).items():
        title = re.sub(r'<[^>]+>','',a.get("titleHtml",""))
        if query and query.lower() not in title.lower(): continue
        articles.append(f"  • {title}\n    https://habr.com/ru/articles/{aid}/")
    return "Habr:\n"+"\n".join(articles[:5]) if articles else "Не найдено"
