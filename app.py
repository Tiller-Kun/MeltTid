import streamlit as st

st.title("🧊 MeltTid")
st.subheader("Understand Everyday Social & Political Standpoints")
st.subheader("With a world with so much information, ")


topic = st.text_input("Enter a topic or keyword:")

if st.button("MELT IT ♨️"):
    st.write("Analyzing:", topic)
    st.write("Summary: (coming soon)")
    st.write("Tone: (coming soon)")
    st.write("Credibility: (coming soon)")


“MeltTid lets users upload short-form political/social videos and instantly see what’s being said, how it’s framed, and how credible it is.”