import requests
from datetime import datetime, timedelta
import praw
import google.generativeai as genai

#675805e1ac0b48caa2778d055ddc1b63 Tyler 
NEWS_API_KEY = "9d4a28ce6fd8435faab2b8980767c800"
GEMINI_API_KEY = "AIzaSyBv8EXo0hU8o3Lvnh4jYk4wy4Ta3PG5"
genai.configure(api_key=GEMINI_API_KEY)

reddit = praw.Reddit(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_SECRET",
    user_agent="MeltTid/1.0"
)

def fetch_recent_articles_advanced(
    topic, 
    num_articles=100,
    days_back=7,
    sources=(
    "bbc-news,"
    "associated-press,"
    "npr,"
    "abc-news,"
    "cbs-news,"
    "nbc-news,"
    "usa-today"
    "al-jazeera-english,"
    "dw,"
    "france-24,"
    "rt-news"
),      # e.g., "bbc-news,cnn,reuters"
    exclude_domains=(
    "buzzfeed.com,"
    "dailymail.co.uk,"
    "the-sun.co.uk,"
    "tmz.com"
    "foxnews.com,"
    "breitbart.com,"
    "dailycaller.com,"
    "msnbc.com,"
    "occupydemocrats.com"
    "medium.com,"
    "substack.com,"
    "wordpress.com,"
    "blogspot.com"
    ),  # e.g., "example.com"
    search_in=None     # "title", "description", or "content"
):
    
    
    from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
    
    # Build query string
    params = {
        'q': topic,
        'from': from_date,
        'sortBy': 'publishedAt',  # or 'relevancy' or 'popularity'
        'language': 'en',
        'pageSize': min(num_articles, 100),
        'apiKey': NEWS_API_KEY
    }
    
    # Optional controls
    if sources:
        params['sources'] = sources  # Only these sources
    
    if exclude_domains:
        params['excludeDomains'] = exclude_domains  # Block spam sites
    
    if search_in:
        params['searchIn'] = search_in  # Where to search
    
    url = "https://newsapi.org/v2/everything"
    response = requests.get(url, params=params)
    
    if response.status_code != 200:
        return []
    
    articles = response.json().get('articles', [])
    
    # Clean up results
    return [a for a in articles 
            if a.get('title') != '[Removed]' 
            and a.get('url')
            and a.get('description')]


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

def summarize_articles2(articles):
    """
    Generate an AI-powered summary of news articles using Claude API
    """
    
    if not articles:
        return "No recent news found for this topic."
    
    # Prepare article content for Claude
    article_texts = []
    for i, article in enumerate(articles[:5], 1):  # Limit to top 5 articles
        title = article.get('title', 'No title')
        description = article.get('description', '')
        content = article.get('content', '')
        source = article.get('source', {}).get('name', 'Unknown')
        
        # Combine available text
        text = f"Article {i} ({source}):\n{title}\n{description}"
        if content:
            text += f"\n{content[:500]}"  # First 500 chars of content
        
        article_texts.append(text)
    
    # Combine all articles
    combined_text = "\n\n---\n\n".join(article_texts)
    
    # Call Claude API for summarization
    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 1000,
                "messages": [
                    {
                        "role": "user",
                        "content": f"""Summarize these news articles into a cohesive 3-4 paragraph summary. 
Focus on:
1. The main event or story
2. Key facts and developments
3. Different perspectives or reactions
4. Why this matters

Articles:
{combined_text}

Provide a clear, engaging summary that captures the essence of what's happening."""
                    }
                ]
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            summary = data['content'][0]['text']
            return summary
        else:
            # Fallback to simple summary if API fails
            return create_simple_summary(articles)
            
    except Exception as e:
        print(f"Error calling Claude API: {e}")
        return create_simple_summary(articles)


def create_simple_summary(articles):
    """
    Fallback summary method if AI API fails
    """
    if not articles:
        return "No recent news found for this topic."
    
    summary = f"Found {len(articles)} recent articles on this topic:\n\n"
    
    for i, article in enumerate(articles[:5], 1):
        title = article.get('title', 'No title')
        source = article.get('source', {}).get('name', 'Unknown')
        description = article.get('description', 'No description available')
        
        summary += f"{i}. **{title}** ({source})\n"
        summary += f"   {description[:200]}...\n\n"
    
    return summary

def get_reddit_perspectives(topic, num_posts=30):
    """
    Get diverse Reddit perspectives with actual quotes from users
    Returns different viewpoints with supporting quotes
    """
    reactions = []
    
    # Search across all of Reddit
    for submission in reddit.subreddit("all").search(topic, limit=num_posts, sort='top', time_filter='week'):
        submission.comments.replace_more(limit=0)
        top_comments = submission.comments[:15]
        
        reaction = {
            'platform': 'Reddit',
            'subreddit': submission.subreddit.display_name,
            'title': submission.title,
            'text': submission.selftext,
            'score': submission.score,
            'num_comments': submission.num_comments,
            'url': f"https://reddit.com{submission.permalink}",
            'comments': []
        }
        
        for comment in top_comments:
            if hasattr(comment, 'body') and len(comment.body) > 50:
                reaction['comments'].append({
                    'text': comment.body,
                    'score': comment.score,
                    'author': str(comment.author)
                })
        
        reactions.append(reaction)
    
    return reactions


# ────────────────────────────────────────────────
#  Updated: Gemini version of analyze_reddit_sentiment
# ────────────────────────────────────────────────

def analyze_reddit_sentiment(topic):
    """
    Analyze Reddit reactions and extract diverse perspectives with quotes using Gemini
    Returns 3 different viewpoints with supporting quotes
    """
    reactions = get_reddit_perspectives(topic, num_posts=30)
    
    if not reactions:
        return {
            'perspectives': [],
            'error': 'No Reddit discussions found for this topic'
        }
    
    # Prepare Reddit content (same as before)
    reddit_content = f"Topic: {topic}\n\n"
    
    for i, reaction in enumerate(reactions[:15], 1):
        reddit_content += f"POST {i} (r/{reaction['subreddit']}, {reaction['score']} upvotes):\n"
        reddit_content += f"Title: {reaction['title']}\n"
        
        if reaction['text']:
            reddit_content += f"Post: {reaction['text'][:300]}\n"
        
        reddit_content += "Top Comments:\n"
        for j, comment in enumerate(reaction['comments'][:5], 1):
            reddit_content += f" Comment {j} ({comment['score']} upvotes): {comment['text'][:200]}\n"
        
        reddit_content += "\n---\n\n"
    
    # Gemini prompt — very similar structure
    prompt = f"""Analyze these Reddit discussions about "{topic}" and identify **exactly 3 DIFFERENT perspectives/viewpoints**.

For each perspective:
1. Give it a clear label (e.g. "Strongly Supportive", "Highly Critical", "Skeptical but Open", "Concerned about X", "Neutral/Pragmatic", etc.)
2. Explain the viewpoint in 2–3 concise sentences
3. Include 2–3 direct quotes from Reddit users that best represent this view (keep each quote under 100 words)

Focus on **real diversity** — include opposing or contrasting views when they exist.

Return **ONLY valid JSON** — nothing else — in this exact structure:

{{
  "perspectives": [
    {{
      "label": "Perspective Name",
      "summary": "2-3 sentence explanation",
      "quotes": [
        {{
          "text": "Exact quote text here",
          "context": "r/subreddit, X upvotes"
        }},
        ...
      ]
    }},
    ...
  ]
}}

Reddit Content:
{reddit_content}
"""

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")  # or "gemini-1.5-pro" if you prefer

        response = model.generate_content(prompt)
        text = response.text.strip()

        # Clean up common markdown fences Gemini sometimes adds
        if text.startswith("```"):
            text = text.split("```json", 1)[-1].rsplit("```", 1)[0].strip()

        result = json.loads(text)

        # Basic validation
        if not isinstance(result, dict) or "perspectives" not in result:
            raise ValueError("Missing 'perspectives' key in response")

        return result

    except json.JSONDecodeError as e:
        print(f"JSON Parse Error: {e}\nRaw response:\n{text}")
        return {
            'perspectives': [],
            'error': 'Failed to parse JSON from Gemini',
            'raw_response': text
        }
    except Exception as e:
        print(f"Gemini error: {e}")
        return {
            'perspectives': [],
            'error': str(e)
        }