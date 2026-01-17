# gemini_utils.py
import google.generativeai as genai
import os

GEMINI_API_KEY = "AIzaSyBv8EXo0hU8o3Lvnh4jYk4wy4Ta3PG5-GA"
genai.configure(api_key=GEMINI_API_KEY)

def gemini_analyze_transcript(transcript: str) -> str:
    if not transcript or not transcript.strip():
        return "No transcript provided."

    prompt = f"""
You are MeltTid, a platform that helps people understand social and political media.

Given the following transcript:
----------------
{transcript}
----------------

Return:
1) A concise summary (2–4 sentences)
2) Emotional tone / sentiment
3) Framing / bias style (persuasive, neutral, alarmist, opinionated)
4) Likely audience reaction (bullet points)
5) Keywords

Respond EXACTLY in this format:

Summary:
...

Sentiment:
...

Framing:
...

Likely audience reaction:
- ...
- ...

Keywords:
- ...
- ...
- ...
- ...
- ...
"""

    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    return response.text

def analyze_video_with_gemini(video_bytes: bytes) -> str:
    """
    Sends a video file to Gemini and returns a structured analysis:
    - Summary
    - Tone
    - Sentiment
    - Framing / Bias
    """

    model = genai.GenerativeModel("gemini-1.5")

    prompt = """
    Analyze this video and return:

    1. A concise summary of the content.
    2. The speaker’s tone (e.g. calm, angry, persuasive, sarcastic, emotional).
    3. The overall sentiment (positive, negative, neutral, mixed).
    4. Any persuasive, biased, or emotionally manipulative framing used.

    Be clear, structured, and brief.
    """

    response = model.generate_content([
        {
            "role": "user",
            "parts": [
                {"text": prompt},
                {
                    "inline_data": {
                        "mime_type": "video/mp4",
                        "data": video_bytes
                    }
                }
            ]
        }
    ])

    return response.text
