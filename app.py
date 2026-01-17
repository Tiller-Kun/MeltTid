import streamlit as st

st.title("🧊 MeltTid")
st.subheader("Understand Everyday Social & Political Standpoints")
st.subheader("With a world with so much information, ")

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
            st.write("Analyzing:", topic)
            # Placeholder for actual analysis
            st.write("Summary: (coming soon)")
            st.write("Tone: (coming soon)")
            st.write("Credibility: (coming soon)")

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
