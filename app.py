import streamlit as st
import pickle
import pandas as pd
import requests

# download movie_dict.pkl and similarity.pkl and paste them to this directory before running the app


def fetch_poster(movie_id):
    api_key = "e06818a170de34c6c96230794fb70781"  # ideally store in st.secrets or env var
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
    response = requests.get(url)
    if response.status_code != 200:
        # handle error, e.g., return a placeholder image URL or None
        return None
    data = response.json()
    poster_path = data.get('poster_path')
    if not poster_path:
        return None
    return "https://image.tmdb.org/t/p/w500/" + poster_path

movies_list = pickle.load(open('movie_dict.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))
movies = pd.DataFrame(movies_list)

st.title("Movie Recommender System")

selected_movie_name = st.selectbox('select movie', movies['title'].values)

print(type(selected_movie_name))


def recommend(movie):
  movie_index = movies[movies['title'] == movie].index[0]
  distances = similarity[movie_index]
  reco_list = sorted(list(enumerate(distances)), reverse=True, key = lambda x:x[1])[1:11]
  reco_titles = []
  reco_posters = []
  for i in reco_list:
      movie_id = movies.iloc[i[0]].movie_id
      reco_titles.append(movies.iloc[i[0]].title)
      # fetch poster from API
      reco_posters.append(fetch_poster(movie_id))
  return reco_titles, reco_posters

if st.button('Recommend movie'):
#    st.write(selected_movie_name)
    names, posters = recommend(selected_movie_name)
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.text(names[0])
        st.image(posters[0])
    with col2:
        st.text(names[1])
        st.image(posters[1])
    with col3:
        st.text(names[2])
        st.image(posters[2])
    with col4:
        st.text(names[3])
        st.image(posters[3])
    with col5:
        st.text(names[4])
        st.image(posters[4])
    col6, col7, col8, col9, col10 = st.columns(5)
    with col6:
        st.text(names[5])
        st.image(posters[5])
    with col7:
        st.text(names[6])
        st.image(posters[6])
    with col8:
        st.text(names[7])
        st.image(posters[7])
    with col9:
        st.text(names[8])
        st.image(posters[8])
    with col10:
        st.text(names[9])
        st.image(posters[9])