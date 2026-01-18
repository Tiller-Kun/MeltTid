# ** MeltTid **

# In today’s day and age, social-political opinions run vast, but how can we understand the people actually engaging with social media and their sentimental responses?
# MeltTid reveals those tidbits.

Our project, MeltTid, was inspired by the fast-moving, often frightening news and social media cycle and the desire to understand how people react to political and emotional content on various media platforms. 
Using the skills we developed in Williams CS courses, and the strengths of todays LLM's and API's we built a Python-based Streamlit platform that pulls data from multiple APIs and makes it easy to analyze, scalable for more social media platforms. 
We combine AI tools with well-rounded, reliable sources. Along the way, we faced challenges in gathering relevant data, debugging with bot walls or api limits, and making sense of diverse opinions, but these obstacles taught us how to integrate technology, critical thinking, and our education to make sense of a complex world while staying grounded in trustworthy information and that the sentimental voices of people matter.

🚀 Setup & Installation
To run MeltTid locally, you’ll need API keys and Python libraries.

1️⃣ Get API Keys
Create accounts and generate keys for:
NewsAPI → https://newsapi.org
Google Gemini API → https://ai.google.dev
ScrapeCreators API → https://scrapecreators.com
X (Twitter) API → https://developer.x.com

2️⃣ Set Environment Variables (sample test ones are shown but are not for public use)
export NEWS_API_KEY="your_key_here"
export GEMINI_API_KEY="your_key_here"
export SCRAPECREATORS_API_KEY="your_key_here"
export X_API_KEY="your_key_here"
export X_API_SECRET="your_secret_here"
(Windows users: use set instead of export)

3️⃣ Install Dependencies
pip install streamlit scikit-learn requests python-dotenv

4️⃣ Run the App
streamlit run app.py
