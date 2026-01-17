import streamlit as st
import time
from search_utils import rank_by_similarity
from search_module import fetch_recent_articles, summarize_articles2, fetch_recent_articles_advanced, analyze_reddit_sentiment
from video_utils import fetch_tiktok_transcript, fetch_instagram_transcript


# Splash container and state check
if 'splash_done' not in st.session_state:
    st.session_state.splash_done = False

if not st.session_state.splash_done:
    splash = st.empty()

    animation_text = ["🧊 MeltTid", "💧 MeltTid.", "🧊 MeltTid..", "💧 MeltTid..."]

    for i in range(4):  # 4 frames (~2 sec)
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

    splash.empty()
    st.session_state.splash_done = True  # Mark splash as done

# OPENING Header

st.title("🧊 MeltTid")
st.subheader("Understand Everyday Social & Political Standpoints")
st.subheader("With a world with so much information anyone can get summaries, but what about the sentimental tidbits?")


# Create tabs
tab1, tab2, tab3 = st.tabs(["General Search 🔍", "Video Submission 🎥", "Social Media Links 🔗"])

# General Search
with tab1:
    st.header("General Search")
    st.write("Enter a specific topic with keywords to analyze text-based content.")
    
    topic = st.text_input("Topic or keyword:")
    
    if st.button("MELT IT ♨️", key="search"):
        if topic.strip() == "":
            st.warning("Please enter a topic!")
        else:
            st.write("Analyzing...", topic)
            # Fetch articles
            raw_articles = fetch_recent_articles(topic, num_articles=20)
            advanced_articles = fetch_recent_articles_advanced(topic, num_articles=100)

            # Rank both sets by similarity
            ranked_raw = rank_by_similarity(raw_articles, topic)
            ranked_advanced = rank_by_similarity(advanced_articles, topic)

            # Filter relevant articles
            relevant_raw = [a for a, score in ranked_raw if score > 0.1][:5]
            relevant_advanced = [a for a, score in ranked_advanced if score > 0.1][:5]

            # Display in columns
            col1, col2 = st.columns(2)

            # Left column Summary of advanced / highly relevant articles
            with col1:
                st.subheader("Summary")
                if relevant_advanced:
                    summary = summarize_articles2(relevant_advanced)
                    st.info(summary)                    
                else:
                    st.info("No highly relevant articles to summarize.")

            
            # Right column Sources
            with col2:
                st.subheader("Sources Advanced")
                if relevant_advanced:
                    for a in relevant_advanced:
                        st.markdown(f"- [{a['title']}]({a['url']}) ({a['source']['name']})")
                else:
                    st.info("No highly relevant advanced articles found.")

                st.subheader("Sources Raw")
                if relevant_raw:
                    for a in relevant_raw:
                        st.markdown(f"- [{a['title']}]({a['url']}) ({a['source']['name']})")
                else:
                    st.info("No relevant raw articles found.")
                    
            #REDDIT 
            st.markdown("---")
            st.subheader("💬 What People Are Saying (Reddit)")
            
            with st.spinner("Analyzing Reddit discussions..."):
                reddit_analysis = analyze_reddit_sentiment(topic)
            
            if reddit_analysis.get('error'):
                st.warning(f"Could not analyze Reddit sentiment: {reddit_analysis['error']}")
            elif not reddit_analysis.get('perspectives'):
                st.info("No Reddit discussions found for this topic.")
            else:
                # Display each perspective in its own section
                perspectives = reddit_analysis['perspectives']
                
                for i, perspective in enumerate(perspectives, 1):
                    # Create expander for each perspective
                    with st.expander(f"**{perspective['label']}** 👥", expanded=(i==1)):
                        st.write(perspective['summary'])
                        
                        if perspective.get('quotes'):
                            st.markdown("**Representative Quotes:**")
                            for quote in perspective['quotes']:
                                # Display quote in a nice format
                                st.markdown(f"""
                                > *"{quote['text']}"*
                                
                                {quote['context']}
                                """)
                                st.markdown("")  # Spacing

# Video Submission
with tab2:
    st.header("Video Submission")
    st.write("Upload a longer political/social video to analyze its content.")
    
    uploaded_file = st.file_uploader("Upload a video", type=["mp4", "mov"])
    
    if uploaded_file is not None:
        st.video(uploaded_file)
        
        if st.button("MELT IT ♨️", key="video"):
            # Placeholder for actual video analysis
            st.write("Analyzing uploaded video...")
            st.write("Summary: (coming soon)")
            st.write("Tone: (coming soon)")
            st.write("Credibility: (coming soon)")

with tab3:
    st.header("Social Media Video → MeltTid Down!")

    video_url = st.text_input("Paste a TikTok or Instagram video/reel URL")

    if st.button("Transcribe Video"):
        if not video_url.strip():
            st.warning("Please enter a valid URL")
        else:
            # Determine platform
            if "tiktok.com" in video_url:
                fetch_fn = fetch_tiktok_transcript
                platform_name = "TikTok"
            elif "instagram.com" in video_url:
                fetch_fn = fetch_instagram_transcript
                platform_name = "Instagram"
            else:
                st.error("Unsupported platform. Only TikTok and Instagram are supported currently.")
                fetch_fn = None

            if fetch_fn:
                with st.spinner(f"Fetching transcript from {platform_name} (this can take 10–30s)..."):
                    try:
                        # Call the appropriate fetch function
                        if platform_name == "TikTok":
                            data = fetch_fn(video_url, SCRAPECREATORS_API_KEY)
                            transcript = data.get("transcript", "")
                        else:  # Instagram
                            data = fetch_fn(video_url, SCRAPECREATORS_API_KEY)
                            transcripts = data.get("transcripts", [])
                            transcript = " ".join([t.get("text", "") for t in transcripts])

                        # Display transcript & analysis
                        if transcript.strip():
                            st.subheader("Transcript")
                            st.write(transcript)

                            st.subheader("Melted Analysis")
                            st.write(summarize_text(transcript))
                        else:
                            st.warning("No transcript found for this video.")
                    except Exception as e:
                        st.error(f"Error fetching transcript: {e}")

