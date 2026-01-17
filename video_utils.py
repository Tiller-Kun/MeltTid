
import requests

SCRAPECREATORS_API_KEY = "MGnFdOTLWNb17FtwCJVUZqoNFAQ2"

def fetch_tiktok_transcript(tiktok_url):
    """
    Fetches TikTok video transcript using ScrapeCreators API.
    """
    endpoint = "https://api.scrapecreators.com/v1/tiktok/video/transcript"

    params = {
        "url": tiktok_url,
        "use_ai_as_fallback": "false"   # Credit-safe setting
    }

    headers = {
        "x-api-key": SCRAPECREATORS_API_KEY,
        "Content-Type": "application/json"
    }

    response = requests.get(endpoint, headers=headers, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def fetch_instagram_transcript(instagram_url):
    """
    Fetches Instagram post/reel transcript using ScrapeCreators API.
    """
    endpoint = "https://api.scrapecreators.com/v2/instagram/media/transcript"

    params = {
        "url": instagram_url
    }

    headers = {
        "x-api-key": SCRAPECREATORS_API_KEY,
        "Content-Type": "application/json"
    }

    response = requests.get(endpoint, headers=headers, params=params, timeout=30)
    response.raise_for_status()
    return response.json()
