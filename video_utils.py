import requests

def fetch_tiktok_transcript(tiktok_url, api_key):
    endpoint = "https://api.scrapecreators.com/v1/tiktok/video/transcript"

    params = {
        "url": tiktok_url,
        "use_ai_as_fallback": "false"   # Credit-safe setting
    }

    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json"
    }

    response = requests.get(endpoint, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

def fetch_instagram_transcript(instagram_url, api_key):
    endpoint = "https://api.scrapecreators.com/v2/instagram/media/transcript"

    params = {
        "url": instagram_url
    }

    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json"
    }

    response = requests.get(endpoint, headers=headers, params=params)
    response.raise_for_status()
    return response.json()