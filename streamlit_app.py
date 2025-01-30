import streamlit as st
import pandas as pd
from google.cloud import firestore
from google.oauth2 import service_account
import json

# Cargar credenciales desde el archivo de secretos
key_dict = json.loads(st.secrets["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds, project="movies-reto-43af9")

dbMovies = db.collection("movies")

st.sidebar.header("Menú de opciones")

# Checkbox para mostrar todas las películas
toggle_all_movies = st.sidebar.checkbox("Mostrar todas las películas")

if toggle_all_movies:
    movies_ref = list(dbMovies.stream())
    movies_dict = list(map(lambda x: x.to_dict(), movies_ref))
    movies_dataframe = pd.DataFrame(movies_dict)
    st.dataframe(movies_dataframe)

# ----------------- BÚSQUEDA POR TÍTULO ----------------- #
st.sidebar.subheader("Buscar película por título")
title_search = st.sidebar.text_input("Título de la película")
btn_search = st.sidebar.button("Buscar")

def search_movie_by_title(title):
    movies_ref = dbMovies.where("title", ">=", title).where("title", "<=", title + "\uf8ff").stream()
    return [movie.to_dict() for movie in movies_ref]

if btn_search and title_search:
    results = search_movie_by_title(title_search.lower())
    if results:
        st.dataframe(pd.DataFrame(results))
    else:
        st.sidebar.write("No se encontraron coincidencias.")

# ----------------- FILTRAR POR DIRECTOR ----------------- #
st.sidebar.subheader("Filtrar por director")

# Obtener la lista de directores únicos
directors_ref = list(dbMovies.stream())
directors = sorted(set(movie.to_dict().get("director", "") for movie in directors_ref))

director_selected = st.sidebar.selectbox("Selecciona un director", directors)
btn_filter_director = st.sidebar.button("Filtrar")

def filter_by_director(director):
    movies_ref = dbMovies.where("director", "==", director).stream()
    return [movie.to_dict() for movie in movies_ref]

if btn_filter_director and director_selected:
    filtered_movies = filter_by_director(director_selected)
    if filtered_movies:
        st.dataframe(pd.DataFrame(filtered_movies))
        st.sidebar.write(f"Total de películas encontradas: {len(filtered_movies)}")
    else:
        st.sidebar.write("No se encontraron películas para este director.")

# ----------------- FORMULARIO PARA INSERTAR PELÍCULA ----------------- #
st.sidebar.subheader("Agregar nueva película")
new_title = st.sidebar.text_input("Título")
new_director = st.sidebar.text_input("Director")
new_year = st.sidebar.text_input("Año de lanzamiento")
new_genre = st.sidebar.text_input("Género")
btn_add_movie = st.sidebar.button("Agregar película")

if btn_add_movie and new_title and new_director and new_year and new_genre:
    new_movie = {
        "title": new_title,
        "director": new_director,
        "year": new_year,
        "genre": new_genre,
    }
    dbMovies.add(new_movie)
    st.sidebar.success("Película agregada correctamente")
