import streamlit as st
import json
from src.questioner import ask_news_question, question_exampler
from src.searcher import search
import pandas as pd

# Set page config
st.set_page_config(
    page_title="CHRONOS News Timeline Generator",
    page_icon="📰",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .news-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
    .question-card {
        background-color: #e1e5eb;
        border-radius: 10px;
        padding: 15px;
        margin: 5px 0;
    }
    .source-link {
        color: #4a90e2;
        text-decoration: none;
        font-size: 0.9em;
        margin-top: 10px;
        display: inline-block;
    }
    .source-link:hover {
        text-decoration: underline;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.title("📰 CHRONOS News Timeline Generator")
st.markdown("---")

# Input section
col1, col2 = st.columns([2, 1])
with col1:
    topic = st.text_input("Enter your topic of interest:", placeholder="e.g., Ukraine Crisis")
with col2:
    num_questions = st.number_input("Number of questions to generate:", min_value=1, max_value=10, value=5)
    num_results = st.number_input("Number of search results:", min_value=5, max_value=50, value=20)

if topic:
    with st.spinner("🔍 Searching for relevant information..."):
        # Search for documents
        docs = search([topic], n_max_doc=num_results)
        
        if docs:
            # Generate questions
            questions = ask_news_question('gpt-3.5-turbo', topic, docs=docs)
            
            # Display results
            st.markdown("### 📊 Timeline Overview")
            
            # Create timeline
            timeline_data = []
            for doc in docs:
                timeline_data.append({
                    'Date': pd.to_datetime(doc['timestamp']).strftime('%Y-%m-%d'),
                    'Title': doc['title'],
                    'Content': doc['snippet'],
                    'URL': doc['url']
                })
            
            df = pd.DataFrame(timeline_data)
            df = df.sort_values('Date')
            
            # Display timeline
            for _, row in df.iterrows():
                with st.container():
                    st.markdown(f"""
                    <div class='news-card'>
                        <h4>{row['Date']}</h4>
                        <h3>{row['Title']}</h3>
                        <p>{row['Content']}</p>
                        <a href="{row['URL']}" target="_blank" class="source-link">📄 Read full article</a>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Display generated questions
            if questions:
                st.markdown("### ❓ Generated Questions")
                for q in questions[:num_questions]:
                    st.markdown(f"""
                    <div class='question-card'>
                        {q}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("No questions could be generated. Try adjusting your topic.")
        else:
            st.error("No relevant information found. Try a different topic or adjust your search terms.")