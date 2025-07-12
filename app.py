import streamlit as st
import pickle
import pandas as pd
import requests
import os
import difflib

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────
# Hardcode your TMDB API key here (replace with your actual key).
TMDB_API_KEY = os.getenv("API_KEY")

# Streamlit page settings
st.set_page_config(
    page_title="🎬 Movie Recommender",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────────────────────
# CSS: Light theme background with dark text
# ─────────────────────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    try:
        movies_list = pickle.load(open('movie_dict.pkl', 'rb'))
        similarity = pickle.load(open('similarity.pkl', 'rb'))
    except FileNotFoundError as e:
        st.error(f"Data files not found: {e}")
        return None, None
    df = pd.DataFrame(movies_list)
    return df, similarity

movies, similarity = load_data()
if movies is None or similarity is None:
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR CONTROLS
# ─────────────────────────────────────────────────────────────────────────────
st.sidebar.header("🔎 Filters & Search")
search_input = st.sidebar.text_input("Search Movie Title (partial)")
num_recs = st.sidebar.slider("Number of recommendations", 5, 20, 10)

# ─────────────────────────────────────────────────────────────────────────────
# MAIN CONTENT
# ─────────────────────────────────────────────────────────────────────────────
st.title("Movie Recommender System")

# Movie selector with optional fuzzy matching
all_titles = movies['title'].tolist()
if search_input:
    matches = difflib.get_close_matches(search_input, all_titles, n=10, cutoff=0.5)
    if matches:
        selected_movie = st.selectbox("Select a movie", matches)
    else:
        st.warning("No matches found. Showing full list.")
        selected_movie = st.selectbox("Select a movie", all_titles)
else:
    selected_movie = st.selectbox("Select a movie", all_titles)

# ─────────────────────────────────────────────────────────────────────────────
# POSTER FETCHING (CACHED)
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=24*3600)
def fetch_poster(movie_id: int):
    if not TMDB_API_KEY or not movie_id:
        return None
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
    except requests.RequestException:
        return None
    data = resp.json()
    path = data.get('poster_path')
    return f"https://image.tmdb.org/t/p/w500{path}" if path else None

# ─────────────────────────────────────────────────────────────────────────────
# RECOMMENDATION LOGIC (CACHED)
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data
def recommend(movie: str, top_n: int = 10):
    try:
        idx = movies[movies['title'] == movie].index[0]
    except IndexError:
        return [], []
    distances = similarity[idx]
    ranked = sorted(enumerate(distances), key=lambda x: x[1], reverse=True)[1:top_n+1]
    titles, posters = [], []
    for i, _ in ranked:
        row = movies.iloc[i]
        titles.append(row['title'])
        mid = row.get('movie_id') or row.get('id') or row.get('movieId')
        posters.append(fetch_poster(mid))
    return titles, posters

# ─────────────────────────────────────────────────────────────────────────────
# RUN RECOMMENDATION ON BUTTON CLICK
# ─────────────────────────────────────────────────────────────────────────────
if st.button("Recommend Movie"):
    if not selected_movie:
        st.error("Please choose a movie first.")
    else:
        with st.spinner("Fetching recommendations..."):
            rec_titles, rec_posters = recommend(selected_movie, top_n=num_recs)
        if not rec_titles:
            st.warning("No recommendations could be generated.")
        else:
            cols = st.columns(5)
            for idx, (title, poster_url) in enumerate(zip(rec_titles, rec_posters)):
                col = cols[idx % 5]
                with col:
                    st.caption(title)
                    if poster_url:
                        st.image(poster_url, use_container_width=True)
                    else:
                        st.info("No image available")
                if (idx + 1) % 5 == 0 and (idx + 1) < len(rec_titles):
                    cols = st.columns(5)

# ─────────────────────────────────────────────────────────────────────────────
# DEPENDENCIES
# ─────────────────────────────────────────────────────────────────────────────
# streamlit, pandas, requests, difflib
