from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def rank_by_similarity(articles, topic):
    # Handle empty articles list
    if not articles:
        return []
    
    docs = [
        f"{a.get('title','')} {a.get('description','')} {a.get('source',{}).get('name','')}"
        for a in articles
        if a.get('title') or a.get('description')
    ]

    # Handle case where no valid docs exist after filtering
    if not docs:
        return []
    
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf = vectorizer.fit_transform([topic] + docs)

    similarities = cosine_similarity(tfidf[0:1], tfidf[1:])[0]

    ranked = sorted(
        zip(articles, similarities),
        key=lambda x: x[1],
        reverse=True
    )

    return ranked
