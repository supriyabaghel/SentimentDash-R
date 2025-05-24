
import streamlit as st
import praw
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Sentiment Dashboard", layout="wide")


st.markdown("""
    <style>
        .footer {
            position: fixed;
            bottom: 10px;
            right: 10px;
            background-color: black;
            color: pink;
            padding: 6px 12px;
            border-radius: 12px;
            font-weight: bold;
            font-size: 12px;
            z-index: 100;
        }
        .st-emotion-cache-1v0mbdj {
            padding-bottom: 60px;
        }
    </style>
    <div class="footer">Developed by Supriya</div>
""", unsafe_allow_html=True)


st.sidebar.title("🔍 Sentiment Analyzer")
with st.sidebar.form(key="search_form"):
    topic = st.text_input("Enter a topic:", "AI")
    limit = st.slider("Number of posts to analyze", min_value=10, max_value=100, step=10, value=20)
    submit_button = st.form_submit_button(label="🔎 Search")


reddit = praw.Reddit(
    client_id='myid',
    client_secret='mysecret',
    user_agent='sentimentDash by /u/supriyadev3824'
)

analyzer = SentimentIntensityAnalyzer()

def get_sentiment(text):
    score = analyzer.polarity_scores(text)["compound"]
    if score >= 0.05:
        return "Positive"
    elif score <= -0.05:
        return "Negative"
    else:
        return "Neutral"

def search_reddit_by_keyword(keyword="AI", limit=20):
    posts = []
    for post in reddit.subreddit("all").search(keyword, sort="new", limit=limit):
        content = post.title + " " + (post.selftext or "")
        posts.append({"title": post.title, "content": content, "url": post.url})
    return posts

def analyze_keyword_sentiments(posts):
    sentiments = [get_sentiment(post["content"]) for post in posts]
    df = pd.DataFrame(posts)
    df["Sentiment"] = sentiments
    return df


st.title("📊What's the Mood?")

if submit_button and topic:
    with st.spinner("Fetching and analyzing posts..."):
        posts = search_reddit_by_keyword(topic, limit=limit)
        if not posts:
            st.warning("No posts found for this topic.")
        else:
            df = analyze_keyword_sentiments(posts)

        
            st.subheader("🔢 Sentiment Summary")
            col1, col2, col3 = st.columns(3)
            col1.metric("😄 Positive", df["Sentiment"].value_counts().get("Positive", 0))
            col2.metric("😐 Neutral", df["Sentiment"].value_counts().get("Neutral", 0))
            col3.metric("😡 Negative", df["Sentiment"].value_counts().get("Negative", 0))

            
            col1, col2 = st.columns([2, 1])
            with col1:
                st.subheader(f"📝 Top {limit} posts for '{topic}':")
                emoji_map = {"Positive": "😄", "Negative": "😡", "Neutral": "😐"}
                for i, row in df.iterrows():
                    st.markdown(f"[{row['title']}]({row['url']})")
                    emoji = emoji_map.get(row["Sentiment"], "")
                    st.write(f"Sentiment: **{row['Sentiment']} {emoji}**")
                    st.markdown("---")

            with col2:
                st.subheader("📊 Sentiment Distribution")
                fig, ax = plt.subplots()
                colors = {'Positive': 'green', 'Neutral': 'gray', 'Negative': 'red'}
                df["Sentiment"].value_counts().plot(
                    kind="bar",
                    color=[colors[s] for s in df["Sentiment"].value_counts().index],
                    ax=ax
                )
                ax.set_xlabel("Sentiment")
                ax.set_ylabel("Number of Posts")
                ax.grid(True)
                st.pyplot(fig)


