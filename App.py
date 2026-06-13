import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="NEWS 4 U AI",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# API KEY
# =====================================================

try:
    API_KEY = st.secrets["NEWSDATA_API_KEY"]
except Exception:
    st.error(
        "❌ NEWSDATA_API_KEY not found.\n\n"
        "Create .streamlit/secrets.toml and add:\n\n"
        'NEWSDATA_API_KEY="YOUR_API_KEY"'
    )
    st.stop()

# =====================================================
# CUSTOM CSS
# =====================================================

st.markdown("""
<style>

.block-container{
    padding-top:1rem;
}

.hero {
    background: linear-gradient(135deg,#2563eb,#7c3aed);
    padding: 2rem;
    border-radius: 20px;
    text-align:center;
    color:white;
    margin-bottom:20px;
}

.hero h1{
    margin:0;
}

.news-card{
    border:1px solid #e5e7eb;
    border-radius:16px;
    padding:15px;
    margin-bottom:15px;
    background-color:rgba(255,255,255,0.02);
}

.metric-container{
    text-align:center;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# HERO SECTION
# =====================================================

st.markdown("""
<div class="hero">
    <h1>📰 NEWS 4 U.ai </h1>
    <p>Search global news, companies, countries and topics in real-time</p>
</div>
""", unsafe_allow_html=True)

# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.title("⚙️ News Filters")

COUNTRIES = {
    "India": "in",
    "United States": "us",
    "United Kingdom": "gb",
    "Australia": "au",
    "Canada": "ca",
    "Germany": "de",
    "France": "fr",
    "Japan": "jp"
}

CATEGORIES = [
    "top",
    "business",
    "technology",
    "sports",
    "science",
    "health",
    "entertainment",
    "world",
    "politics"
]

selected_country = st.sidebar.selectbox(
    "🌍 Country",
    list(COUNTRIES.keys())
)

selected_category = st.sidebar.selectbox(
    "📰 Category",
    CATEGORIES
)

search_term = st.sidebar.text_input(
    "🔍 Search",
    placeholder="Tesla, Apple, OpenAI, Cricket..."
)

article_limit = st.sidebar.slider(
    "📊 Number of Articles",
    min_value=5,
    max_value=50,
    value=20
)

# =====================================================
# FETCH NEWS
# =====================================================

@st.cache_data(ttl=300)
def fetch_news(country, category, search):

    url = "https://newsdata.io/api/1/latest"

    # SEARCH MODE
    if search.strip():

        params = {
            "apikey": API_KEY,
            "q": search,
            "language": "en"
        }

    # COUNTRY MODE
    else:

        params = {
            "apikey": API_KEY,
            "country": country,
            "language": "en"
        }

        if category != "top":
            params["category"] = category

    try:

        response = requests.get(
            url,
            params=params,
            timeout=20
        )

        data = response.json()

        if response.status_code != 200:
            st.error(data)
            return []

        return data.get("results", [])

    except Exception as e:
        st.error(f"Error: {e}")
        return []

# =====================================================
# LOAD DATA
# =====================================================

with st.spinner("Fetching latest news..."):

    articles = fetch_news(
        COUNTRIES[selected_country],
        selected_category,
        search_term
    )

# Remove noisy sources
blocked_sources = [
    "in_ign"
]

articles = [
    article
    for article in articles
    if article.get("source_id") not in blocked_sources
]

articles = articles[:article_limit]

# =====================================================
# METRICS
# =====================================================

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "📰 Articles",
        len(articles)
    )

with col2:
    st.metric(
        "🌍 Country",
        selected_country
    )

with col3:
    st.metric(
        "📂 Category",
        selected_category.title()
    )

st.divider()

# =====================================================
# SOURCE ANALYTICS
# =====================================================

if len(articles) > 0:

    source_names = []

    for article in articles:

        source = article.get(
            "source_id",
            "Unknown"
        )

        source_names.append(source)

    st.subheader("📈 Top Sources")

    source_df = (
        pd.Series(source_names)
        .value_counts()
        .head(10)
    )

    st.bar_chart(source_df)

st.divider()

# =====================================================
# NEWS SECTION
# =====================================================

if len(articles) == 0:

    st.warning(
        "No articles found.\n\n"
        "Try another country, category or search term."
    )

    st.stop()

if search_term:
    st.subheader(
        f"🔍 Results for '{search_term}'"
    )
else:
    st.subheader(
        f"🔥 {selected_country} Headlines"
    )

# =====================================================
# ARTICLE CARDS
# =====================================================

for article in articles:

    title = article.get(
        "title",
        "No Title"
    )

    description = article.get(
        "description",
        "No description available."
    )

    image = article.get("image_url")

    source = article.get(
        "source_id",
        "Unknown"
    )

    article_url = article.get("link")

    pub_date = article.get("pubDate")

    try:

        pub_date = datetime.strptime(
            pub_date,
            "%Y-%m-%d %H:%M:%S"
        ).strftime(
            "%d %b %Y"
        )

    except:
        pass

    with st.container():

        col1, col2 = st.columns(
            [1, 2]
        )

        with col1:

            if image:
                try:
                    st.image(
                        image,
                        use_container_width=True
                    )
                except:
                    pass

        with col2:

            st.markdown(
                f"### {title}"
            )

            st.caption(
                f"🏢 {source} | 📅 {pub_date}"
            )

            st.write(description)

            if article_url:

                st.link_button(
                    "📖 Read Full Article",
                    article_url,
                    use_container_width=True
                )

        st.divider()