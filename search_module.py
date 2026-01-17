import requests
from datetime import datetime, timedelta
import praw


NEWS_API_KEY = "675805e1ac0b48caa2778d055ddc1b63"

reddit = praw.Reddit(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_SECRET",
    user_agent="MeltTid/1.0"
)

def fetch_recent_articles(topic, num_articles=100):
    from_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    to_date = datetime.now().strftime('%Y-%m-%d')
    
    url = (
        f"https://newsapi.org/v2/everything?"
        f"q={topic}&"                          # Your search term
        f"from={from_date}&"                   # Start date
        f"to={to_date}&"                       # End date
        f"sortBy=publishedAt&"                 # Sort by newest first
        f"language=en&"                        # English only
        f"pageSize={min(num_articles, 100)}&" # Max 100 per request
        f"apiKey={NEWS_API_KEY}"
    )
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

def scrape_reddit_reactions(topic, num_posts=50):
    """
    Get Reddit reactions - BEST for authentic sentiment
    """
    reactions = []
    
    # Search across all of Reddit
    for submission in reddit.subreddit("all").search(topic, limit=num_posts, sort='top', time_filter='week'):
        
        # Get post + top comments
        submission.comments.replace_more(limit=0)  # Don't load "load more" comments
        top_comments = submission.comments[:10]
        
        reactions.append({
            'platform': 'Reddit',
            'subreddit': submission.subreddit.display_name,
            'title': submission.title,
            'text': submission.selftext,
            'score': submission.score,
            'num_comments': submission.num_comments,
            'url': f"https://reddit.com{submission.permalink}",
            'comments': [
                {
                    'text': comment.body,
                    'score': comment.score,
                    'author': str(comment.author)
                }
                for comment in top_comments if hasattr(comment, 'body')
            ],
            'created_utc': submission.created_utc
        })
    
    return reactions
