# movie-recommender-website

A movie recommender website (content based recommender system)

1) Combined movie synopsis, genre, and cast/crew names into one feature called 'tags'
2) Used TF/IDF vectorizer to vectorize tags (excluding stopwords)
3) Generated a similarity matrix with similarity scores between movies
4) Created a recommender website using streamlit

How To Run:

1) run Movie_Recommender_System.ipynb
2) type 'streamlit run app.py' on the terminal (make sure terminal is opened in the same directory as the project files)