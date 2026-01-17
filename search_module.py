import requests
from datetime import datetime, timedelta
import praw
import google.generativeai as genai
import json 
import asyncio
import re 
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError 

#Sample API Keys Free and Limited
#675805e1ac0b48caa2778d055ddc1b63 Tyler 
NEWS_API_KEY = "9d4a28ce6fd8435faab2b8980767c800"
GEMINI_API_KEY = "AIzaSyBv8EXo0hU8o3Lvnh4jYk4wy4Ta3PG5-GA"
genai.configure(api_key=GEMINI_API_KEY)
TWITTER_BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAJpX7AEAAAAA%2B4crmsAR7giZ1XAv9xdAKtxnLWM%3D9t6hekgEexYyqWWHvnkbHSx6A6aCrSqgqyi9TzS4o4LIXRFlMe"
headers = {"Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"}

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
        model = genai.GenerativeModel("gemini-2.0-flash")  # or "gemini-1.5-pro" if you prefer

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

#TWITTER
async def get_x_perspectives(topic: str, news_articles=None, num_tweets: int = 50, days_back: int = 7):
    """
    Scrape X posts using HEADLESS browser + smart search terms from news articles
    WITH ANTI-BOT BYPASS STRATEGIES
    
    Args:
        topic: Main search topic
        news_articles: List of news articles to extract keywords from
        num_tweets: Target number of tweets
        days_back: How many days back to search
    """
    reactions = []
    
    # Build smart search query from news articles
    search_terms = [topic]
    
    if news_articles:
        # Extract key terms from news headlines
        for article in news_articles[:3]:  # Use top 3 articles
            title = article.get('title', '')
            # Extract key phrases (simplified - could use NLP)
            important_words = [
                word for word in title.split() 
                if len(word) > 4 and word[0].isupper()
            ][:2]  # Get 2 important capitalized words
            search_terms.extend(important_words)
    
    # Create search query - use OR to get varied results
    query = ' OR '.join(f'"{term}"' for term in search_terms[:5])
    query += ' lang:en -is:retweet'
    
    print(f"[X Search Query]: {query}")

    async with async_playwright() as p:
        # ANTI-BOT STRATEGY 1: Use Chromium instead of WebKit (better compatibility)
        browser = await p.chromium.launch(
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',  # Hide automation
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-web-security',
            ]
        )
        
        # ANTI-BOT STRATEGY 2: More realistic browser context
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},  # Bigger viewport
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',  # Recent Chrome
            locale='en-US',
            timezone_id='America/New_York',
            geolocation={'longitude': -74.0060, 'latitude': 40.7128},  # NYC
            permissions=['geolocation'],
            color_scheme='dark',  # Match typical X users
            extra_http_headers={
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
        )
        
        page = await context.new_page()
        
        # ANTI-BOT STRATEGY 3: Inject scripts to hide automation
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
            
            window.chrome = {
                runtime: {}
            };
        """)

        graphql_responses = []

        def handle_response(response):
            if 'api/graphql' in response.url and 'SearchTimeline' in response.url:
                asyncio.create_task(capture_graphql(response))

        async def capture_graphql(response):
            try:
                if response.status == 200:
                    text = await response.text()
                    graphql_responses.append({'url': response.url, 'json': json.loads(text)})
            except Exception:
                pass

        page.on('response', handle_response)

        # ANTI-BOT STRATEGY 4: Simulate human behavior before searching
        try:
            # First visit X homepage (more natural)
            print("[X Scraper] Visiting homepage first...")
            await page.goto("https://x.com", timeout=3000000, wait_until='domcontentloaded')
            await page.wait_for_timeout(20000)
            
            # Random mouse movements (simulate human)
            await page.mouse.move(100, 200)
            await page.wait_for_timeout(500)
            await page.mouse.move(300, 400)
            await page.wait_for_timeout(300)
            
            # Now go to search page
            print("[X Scraper] Navigating to search...")
            search_url = f"https://x.com/search?q={query.replace(' ', '%20')}&f=live"
            await page.goto(search_url, timeout=45000, wait_until='domcontentloaded')
            
            # ANTI-BOT STRATEGY 5: Longer, more random wait times
            await page.wait_for_timeout(5000 + (hash(topic) % 3000))  # 5-8 seconds, varies by topic
            
        except PlaywrightTimeoutError:
            print("⚠️ Page load timeout — X might be blocking. Trying alternative approach...")
            await browser.close()
            
            # FALLBACK: Try with visible browser if headless fails
            return await get_x_perspectives_visible(topic, news_articles, num_tweets, days_back)

        # Scroll to load more tweets
        loaded = 0
        last_height = await page.evaluate('document.body.scrollHeight')
        max_scrolls = 5  # Limit scrolls to avoid long waits

        for scroll_count in range(max_scrolls):
            if loaded >= num_tweets:
                break
            
            # ANTI-BOT STRATEGY 6: Human-like scrolling
            # Don't scroll all the way - scroll in chunks
            current_scroll = await page.evaluate('window.pageYOffset')
            scroll_amount = 300 + (hash(f"{topic}{scroll_count}") % 200)  # Random 300-500px
            await page.evaluate(f'window.scrollBy(0, {scroll_amount})')
            
            # Random wait time between scrolls (1.5-4 seconds)
            wait_time = 1500 + (hash(f"{scroll_count}{topic}") % 2500)
            await page.wait_for_timeout(wait_time)

            new_height = await page.evaluate('document.body.scrollHeight')
            if new_height == last_height:
                print(f"[X Scraper] Reached end after {scroll_count+1} scrolls")
                break
            last_height = new_height

            # Process captured GraphQL responses
            for res in graphql_responses[:]:
                try:
                    data = res['json']['data']['search_by_raw_query']['search_timeline']['timeline']['instructions']
                    for instr in data:
                        if instr['type'] == 'TimelineAddEntries':
                            for entry in instr['entries']:
                                if 'tweet_results' not in entry.get('content', {}).get('itemContent', {}):
                                    continue
                                    
                                tweet = entry['content']['itemContent']['tweet_results']['result']
                                if 'legacy' not in tweet:
                                    continue

                                legacy = tweet['legacy']
                                user = tweet.get('core', {}).get('user_results', {}).get('result', {}).get('legacy', {})

                                created_str = legacy.get('created_at', '')
                                try:
                                    created = datetime.strptime(created_str, '%a %b %d %H:%M:%S %z %Y')
                                    if created < datetime.now(created.tzinfo) - timedelta(days=days_back):
                                        continue
                                except:
                                    pass

                                reactions.append({
                                    'platform': 'X',
                                    'author': user.get('screen_name', 'unknown'),
                                    'text': legacy.get('full_text', ''),
                                    'created_at': created_str,
                                    'likes': legacy.get('favorite_count', 0),
                                    'retweets': legacy.get('retweet_count', 0),
                                    'replies': legacy.get('reply_count', 0),
                                    'url': f"https://x.com/{user.get('screen_name', 'x')}/status/{legacy.get('id_str', '')}",
                                    'tweet_id': legacy.get('id_str', '')
                                })

                                loaded += 1
                                if loaded >= num_tweets:
                                    break
                except Exception as e:
                    print(f"Parse error: {e}")
                
                graphql_responses.remove(res)

        await browser.close()
        print(f"[X Scraper] Captured {len(reactions)} tweets")

    return reactions[:num_tweets]


# ═══════════════════════════════════════════════
#  FALLBACK: Visible browser if headless blocked
# ═══════════════════════════════════════════════

async def get_x_perspectives_visible(topic: str, news_articles=None, num_tweets: int = 30, days_back: int = 7):
    """
    Fallback: Run with VISIBLE browser if headless gets blocked
    User can see what's happening and manually solve captchas if needed
    """
    print("⚠️ Trying visible browser mode as fallback...")
    
    reactions = []
    search_terms = [topic]
    
    if news_articles:
        for article in news_articles[:3]:
            title = article.get('title', '')
            important_words = [word for word in title.split() if len(word) > 4 and word[0].isupper()][:2]
            search_terms.extend(important_words)
    
    query = ' OR '.join(f'"{term}"' for term in search_terms[:5])
    query += ' lang:en -is:retweet'
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,  # VISIBLE!
            slow_mo=100  # Slower actions (more human-like)
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        )
        
        page = await context.new_page()
        
        graphql_responses = []

        def handle_response(response):
            if 'api/graphql' in response.url and 'SearchTimeline' in response.url:
                asyncio.create_task(capture_graphql(response))

        async def capture_graphql(response):
            try:
                if response.status == 200:
                    text = await response.text()
                    graphql_responses.append({'url': response.url, 'json': json.loads(text)})
            except Exception:
                pass

        page.on('response', handle_response)

        try:
            search_url = f"https://x.com/search?q={query.replace(' ', '%20')}&f=live"
            await page.goto(search_url, timeout=600000)
            
            # Give user time to solve captcha if needed
            print("⏳ Waiting 10+ seconds for page load (solve captcha if shown)...")
            await page.wait_for_timeout(100000)
            
            # Light scrolling
            for i in range(3):
                await page.evaluate('window.scrollBy(0, 400)')
                await page.wait_for_timeout(2000)
                
            # Process responses (same logic)
            loaded = 0
            for res in graphql_responses:
                try:
                    data = res['json']['data']['search_by_raw_query']['search_timeline']['timeline']['instructions']
                    for instr in data:
                        if instr['type'] == 'TimelineAddEntries':
                            for entry in instr['entries']:
                                if 'tweet_results' not in entry.get('content', {}).get('itemContent', {}):
                                    continue
                                    
                                tweet = entry['content']['itemContent']['tweet_results']['result']
                                if 'legacy' not in tweet:
                                    continue

                                legacy = tweet['legacy']
                                user = tweet.get('core', {}).get('user_results', {}).get('result', {}).get('legacy', {})

                                reactions.append({
                                    'platform': 'X',
                                    'author': user.get('screen_name', 'unknown'),
                                    'text': legacy.get('full_text', ''),
                                    'created_at': legacy.get('created_at', ''),
                                    'likes': legacy.get('favorite_count', 0),
                                    'retweets': legacy.get('retweet_count', 0),
                                    'url': f"https://x.com/{user.get('screen_name', 'x')}/status/{legacy.get('id_str', '')}"
                                })
                                loaded += 1
                                if loaded >= num_tweets:
                                    break
                except Exception as e:
                    print(f"Parse error: {e}")
                    
        except Exception as e:
            print(f"Visible browser also failed: {e}")
        
        await browser.close()
        
    return reactions


# ═══════════════════════════════════════════════
#  ALTERNATIVE: Use Twitter API (Recommended!)
# ═══════════════════════════════════════════════
def get_x_perspectives_api2(topic: str, news_articles=None, max_results: int = 50):
    """Use official Twitter/X API v2"""
    
    try:
        import tweepy
    except ImportError:
        print("❌ tweepy not installed. Run: pip install tweepy")
        return []
    
    # This line uses the token you added at the top ↓
    client = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN)
    
    # Build search query
    search_terms = [topic]
    if news_articles:
        for article in news_articles[:3]:
            title = article.get('title', '')
            important_words = [word for word in title.split() if len(word) > 4][:2]
            search_terms.extend(important_words)
    
    query = ' OR '.join(search_terms[:5])
    query += ' -is:retweet lang:en'
    
    # This actually searches Twitter ↓
    tweets = client.search_recent_tweets(
        query=query,
        max_results=min(max_results, 100),
        tweet_fields=['created_at', 'public_metrics', 'author_id'],
        expansions=['author_id'],
        user_fields=['username', 'verified', 'public_metrics']
    )
    
    # Process tweets and return them
    # ... rest of function
def get_x_perspectives_api(topic: str, news_articles=None, max_results: int = 50):
    """
    BEST APPROACH: Use official Twitter/X API v2
    
    Pros:
    - Reliable, no blocking
    - Fast (no scraping)
    - Legal
    
    Cons:
    - Requires API key
    - Free tier: 1500 tweets/month
    - Only last 7 days
    
    Get API key: https://developer.twitter.com/
    """
    try:
        import tweepy
    except ImportError:
        print("❌ tweepy not installed. Run: pip install tweepy")
        return []
    
    # You need to add your bearer token
    TWITTER_BEARER_TOKEN = "YOUR_BEARER_TOKEN_HERE"  # Get from developer.twitter.com
    
    if TWITTER_BEARER_TOKEN == "YOUR_BEARER_TOKEN_HERE":
        print("⚠️ Twitter API not configured. Set TWITTER_BEARER_TOKEN")
        return []
    
    client = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN)
    
    # Build smart query from news
    search_terms = [topic]
    if news_articles:
        for article in news_articles[:3]:
            title = article.get('title', '')
            important_words = [word for word in title.split() if len(word) > 4 and word[0].isupper()][:2]
            search_terms.extend(important_words)
    
    query = ' OR '.join(search_terms[:5])
    query += ' -is:retweet lang:en'
    
    print(f"[Twitter API Query]: {query}")
    
    try:
        tweets = client.search_recent_tweets(
            query=query,
            max_results=min(max_results, 100),
            tweet_fields=['created_at', 'public_metrics', 'author_id'],
            expansions=['author_id'],
            user_fields=['username', 'verified', 'public_metrics']
        )
        
        if not tweets.data:
            return []
        
        users_dict = {user.id: user for user in tweets.includes.get('users', [])}
        
        reactions = []
        for tweet in tweets.data:
            author = users_dict.get(tweet.author_id)
            reactions.append({
                'platform': 'X',
                'author': author.username if author else 'Unknown',
                'text': tweet.text,
                'created_at': str(tweet.created_at),
                'likes': tweet.public_metrics.get('like_count', 0),
                'retweets': tweet.public_metrics.get('retweet_count', 0),
                'url': f"https://twitter.com/user/status/{tweet.id}"
            })
        
        print(f"[Twitter API] Retrieved {len(reactions)} tweets")
        return reactions
        
    except Exception as e:
        print(f"Twitter API error: {e}")
        return []


async def analyze_x_sentiment(topic: str, news_articles=None, use_api: bool = False):
    """
    Analyze X/Twitter sentiment using smart search based on news context
    
    Args:
        topic: Main search topic
        news_articles: Related news articles to inform search
        use_api: If True, use Twitter API instead of scraping (requires API key)
    """
    
    # Try Twitter API first if enabled
    if use_api:
        print("[X Analysis] Using Twitter API...")
        reactions = get_x_perspectives_api(topic, news_articles, max_results=50)
        if reactions:
            # Continue to Gemini analysis below
            pass
        else:
            print("[X Analysis] API failed, falling back to scraping...")
            use_api = False
    
    # Use scraping if API not enabled or failed
    if not use_api:
        try:
            reactions = await get_x_perspectives(topic, news_articles, num_tweets=60, days_back=7)
        except Exception as e:
            print(f"[X Analysis] Scraping failed: {e}")
            return {
                'perspectives': [],
                'error': f'Scraping failed: {str(e)}. Consider using Twitter API instead.'
            }
    
    if not reactions:
        return {
            'perspectives': [],
            'error': 'No X posts captured. Try: 1) Using Twitter API, 2) Different search terms, 3) Waiting a few minutes'
        }
    
    # Prepare content for Gemini
    x_content = f"Topic: {topic}\n\n"
    
    for i, reaction in enumerate(reactions[:20], 1):
        x_content += f"TWEET {i} (@{reaction['author']}, {reaction['likes']} likes, {reaction['retweets']} RTs):\n"
        x_content += f"{reaction['text']}\n\n"
    
    # Gemini analysis
    prompt = f"""Analyze these X/Twitter posts about "{topic}" and identify **exactly 3 DIFFERENT perspectives/viewpoints**.

For each perspective:
1. Give it a clear label
2. Explain the viewpoint in 2-3 sentences
3. Include 2-3 representative tweets (keep under 100 words each)

Return **ONLY valid JSON**:

{{
  "perspectives": [
    {{
      "label": "Perspective Name",
      "summary": "Explanation",
      "quotes": [
        {{
          "text": "Tweet text",
          "context": "@username, X likes"
        }}
      ]
    }}
  ]
}}

X Content:
{x_content}
"""

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        text = response.text.strip()

        if text.startswith("```"):
            text = text.split("```json", 1)[-1].rsplit("```", 1)[0].strip()

        result = json.loads(text)
        
        if not isinstance(result, dict) or "perspectives" not in result:
            raise ValueError("Missing 'perspectives' key")

        return result

    except Exception as e:
        print(f"X analysis error: {e}")
        return {
            'perspectives': [],
            'error': str(e)
        }