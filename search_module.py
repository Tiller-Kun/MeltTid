import requests

NEWS_API_KEY = "675805e1ac0b48caa2778d055ddc1b63"

def fetch_recent_articles(topic, num_articles=5):
    url = f"https://newsapi.org/v2/everything?q={topic}&sortBy=publishedAt&language=en&apiKey={NEWS_API_KEY}"
    response = requests.get(url).json()
    articles = response.get('articles', [])[:num_articles]
    return articles

def summarize_articles(articles):
    # Placeholder summary logic (later replace with AI model)
    if not articles:
        return "No recent news found for this topic."
    summary = "Recent highlights:\n"
    for a in articles:
        summary += f"- {a['title']} ({a['source']['name']})\n"
    return summary