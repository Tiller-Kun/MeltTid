import streamlit as st
import time
from search_utils import rank_by_similarity
from search_module import fetch_recent_articles, summarize_articles2, fetch_recent_articles_advanced, analyze_reddit_sentiment, analyze_x_sentiment, get_x_perspectives_api2 
from video_utils import fetch_tiktok_transcript, fetch_instagram_transcript
from gemini_utils import gemini_analyze_transcript, analyze_video_with_gemini
import os
import asyncio
SCRAPECREATORS_API_KEY = "MGnFdOTLWNb17FtwCJVUZqoNFAQ2"


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
st.subheader("Understand Everyday SocialPolitical Standpoints")
st.subheader("With a world with so much information how can we link summaries and their sentimental tidbits?")


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

           
            #TWITTER :D 

            st.markdown("---")
            st.subheader("🐦 X/Twitter Perspectives")
            
            # Option to use API vs scraping
            use_twitter_api = st.checkbox(
                "Use Twitter API (faster, more reliable, requires free API key)", 
                value=False,
                help="Get free API key at developer.twitter.com. Scraping is slower but works without API."
            )
            
            scraping_status = "Using Twitter API..." if use_twitter_api else "Scraping X (headless, ~30-60s)..."
            
            with st.spinner(scraping_status):
                try:
                    # Pass news articles to inform X search + API option
                    x_result = asyncio.run(analyze_x_sentiment(
                        topic, 
                        news_articles=relevant_advanced,
                        use_api=use_twitter_api  # Toggle API vs scraping
                    ))

                    if x_result.get('error'):
                        st.warning(f"X analysis: {x_result['error']}")
                        
                        # Show helpful tips
                        with st.expander("💡 Troubleshooting X/Twitter Analysis"):
                            st.markdown("""
                            **Why X scraping fails:**
                            - Rate limiting (X detects automated access)
                            - Captcha challenges
                            - Network issues
                            
                            **Solutions:**
                            1. ✅ **Get free Twitter API** (recommended)
                               - Visit: https://developer.twitter.com/
                               - Sign up for free account
                               - Get Bearer Token
                               - Add to `search_module.py`: `TWITTER_BEARER_TOKEN = "your-token"`
                               - Check the box above to use API
                            
                            2. ⏰ **Wait & retry** (rate limits reset)
                            
                            3. 🔍 **Try simpler search terms** (less likely to be blocked)
                            
                            4. 🌐 **Use VPN** (change IP address)
                            """)
                            
                    elif x_result.get('perspectives'):
                        for i, persp in enumerate(x_result['perspectives'], 1):
                            with st.expander(f"**{persp['label']}** 🐦", expanded=(i==1)):
                                st.write(persp['summary'])
                                
                                if persp.get('quotes'):
                                    st.markdown("**Supporting Tweets:**")
                                    for q in persp['quotes']:
                                        st.markdown(f"""
                                        > *"{q['text']}"*
                                        
                                        {q['context']}
                                        """)
                                        st.markdown("")
                    else:
                        st.info("No perspectives extracted from X.")
                        
                except Exception as e:
                    st.error(f"Error during X analysis: {str(e)}")
                    st.caption("💡 Consider using Twitter API instead (free, more reliable)")

# Video Submission
with tab2:
    st.header("Video Submission")
    st.write("Upload a longer political/social video to analyze its content.")

    uploaded_file = st.file_uploader("Upload a video", type=["mp4", "mov", "webm"])

    if uploaded_file is not None:
        st.video(uploaded_file)

        if st.button("MELT IT ♨️", key="video"):
            with st.spinner("Analyzing uploaded video with Gemini..."):
                video_bytes = uploaded_file.read()
                analysis = analyze_video_with_gemini(video_bytes)

            st.subheader("Melted Video Analysis")
            st.write(analysis)


with tab3:
    st.header("Social Media Video → MeltTid Down!")

    video_url = st.text_input("Paste a TikTok or Instagram video/reel URL")

    if st.button("Transcribe Video"):
        if not video_url.strip():
            st.warning("Please enter a valid URL")
        else:
            # Detect platform
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
                        data = fetch_fn(video_url)  # no API key needed now
                        
                        # Extract transcript
                        if platform_name == "TikTok":
                            transcript = data.get("transcript", "")
                        else:  # Instagram
                            transcripts = data.get("transcripts", [])
                            transcript = " ".join([t.get("text", "") for t in transcripts])

                        if transcript.strip():
                            st.subheader("Transcript")
                            st.write(transcript)

                            st.subheader("Melted Analysis")
                            with st.spinner("Melting context + sentiment (Gemini)..."):
                                trimmed = transcript[:12000]  # Gemini has input limits
                                analysis = gemini_analyze_transcript(trimmed)

                            st.write(analysis)
                        else:
                            st.warning("No transcript found for this video.")

                    except ValueError:
                        st.error("Sorry, no articles or transcript could be processed.")
                    except Exception as e:
                        st.error(f"Error fetching transcript: {e}")

