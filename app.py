import streamlit as st
import time

# Splash container
splash = st.empty()

# Animation frames for text
animation_text = ["🧊 MeltTid", "💧 MeltTid.", "🧊 MeltTid..", "💧 MeltTid..."]

for i in range(4):  # loop through frames multiple times (~3 sec)
    frame = animation_text[i % len(animation_text)]
    splash.markdown(
        f"""
        <div style="display:flex; flex-direction:column; justify-content:center; align-items:center; height:300px;">
            <div style="font-size: 80px; animation: spin 2s linear infinite;">🧊</div>
            <div style="color:#006064; font-size:32px; margin-top:10px;">{frame}</div>
        </div>
        <style>
        @keyframes spin {{
            from {{transform: rotate(0deg);}}
            to {{transform: rotate(360deg);}}
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
    time.sleep(0.5)

# After animation, remove splash
splash.empty()

# OPENING Header

st.title("🧊 MeltTid")
st.subheader("Understand Everyday Social & Political Standpoints")
st.subheader("With a world with so much information, ")


from search_module import fetch_recent_articles, summarize_articles

# Create tabs
tab1, tab2 = st.tabs(["General Search 🔍", "Video Submission 🎥"])

# General Search
with tab1:
    st.header("General Search")
    st.write("Enter a topic or keyword to analyze text-based content.")
    
    topic = st.text_input("Topic or keyword:")
    
    if st.button("MELT IT ♨️", key="search"):
        if topic.strip() == "":
            st.warning("Please enter a topic!")
        else:
            st.write("Analyzing...", topic)
            # Fetch recent articles
            articles = fetch_recent_articles(topic)
            
            # Generate a summary
            summary = summarize_articles(articles)
            
            # Display results in columns
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.subheader("Summary")
                st.info(summary)
            
            with col2:
                st.subheader("Tone")
                st.info("Neutral / Slightly Positive")  # Placeholder for future sentiment analysis
            
            with col3:
                st.subheader("Credibility")
                if articles:
                    st.info("High – based on reputable sources")
                else:
                    st.info("No sources found")
            
            # Show list of sources below
            if articles:
                st.subheader("Sources")
                for a in articles:
                    st.markdown(f"- [{a['title']}]({a['url']}) ({a['source']['name']})")

# Video Submission
with tab2:
    st.header("Video Submission")
    st.write("Upload a short political/social video to analyze its content.")
    st.write("MeltTid allows users to upload this short-form content and instantly see what’s being said, how it’s framed, and how credible it is.")
    
    uploaded_file = st.file_uploader("Upload a video", type=["mp4", "mov"])
    
    if uploaded_file is not None:
        st.video(uploaded_file)
        
        if st.button("MELT IT ♨️", key="video"):
            # Placeholder for actual video analysis
            st.write("Analyzing uploaded video...")
            st.write("Summary: (coming soon)")
            st.write("Tone: (coming soon)")
            st.write("Credibility: (coming soon)")
