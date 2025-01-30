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

# ----------------------- SIDEBAR -----------------------
st.sidebar.header("Menú de opciones")

# Checkbox para mostrar todas las películas
toggle_all_movies = st.sidebar.checkbox("Mostrar todas las películas")

# Búsqueda por título
st.sidebar.subheader("Buscar película por título")
title_search = st.sidebar.text_input("Título del filme:")
btn_search = st.sidebar.button("Buscar filmes")

# Filtrar por director
st.sidebar.subheader("Seleccionar Director")
directors_ref = list(dbMovies.stream())
directors = sorted(set(movie.to_dict().get("director", "") for movie in directors_ref if "director" in movie.to_dict()))
director_selected = st.sidebar.selectbox("Selecciona un director", directors)
btn_filter_director = st.sidebar.button("Filtrar director")

# Agregar nueva película
st.sidebar.subheader("Nuevo filme")
new_title = st.sidebar.text_input("Nombre:")
new_director = st.sidebar.text_input("Director:")
new_year = st.sidebar.text_input("Año de lanzamiento:")
new_genre = st.sidebar.text_input("Género:")
btn_add_movie = st.sidebar.button("Agregar película")

# ----------------------- ÁREA PRINCIPAL -----------------------
st.title("Netflix App")

# Mostrar todas las películas si el checkbox está activado
if toggle_all_movies:
    movies_ref = list(dbMovies.stream())
    movies_dict = list(map(lambda x: x.to_dict(), movies_ref))
    movies_dataframe = pd.DataFrame(movies_dict)
    
    if not movies_dataframe.empty:
        st.write(f"**Total filmes mostrados:** {len(movies_dataframe)}")
        st.dataframe(movies_dataframe)
    else:
        st.write("No hay filmes en la base de datos.")

# Buscar película por título
if btn_search and title_search:
    movies_ref = dbMovies.where("title", ">=", title_search).where("title", "<=", title_search + "\uf8ff").stream()
    results = [movie.to_dict() for movie in movies_ref]

    if results:
        df_results = pd.DataFrame(results)
        st.write(f"**Total filmes encontrados:** {len(df_results)}")
        st.dataframe(df_results)
    else:
        st.write("No se encontraron películas con ese título.")

# Filtrar por director
if btn_filter_director and director_selected:
    filtered_movies = dbMovies.where("director", "==", director_selected).stream()
    filtered_results = [movie.to_dict() for movie in filtered_movies]

    if filtered_results:
        df_filtered = pd.DataFrame(filtered_results)
        st.write(f"**Total de filmes de {director_selected}:** {len(df_filtered)}")
        st.dataframe(df_filtered)
    else:
        st.write("No se encontraron películas para este director.")

# Agregar nueva película
if btn_add_movie and new_title and new_director and new_year and new_genre:
    new_movie = {
        "title": new_title,
        "director": new_director,
        "year": new_year,
        "genre": new_genre,
    }
    dbMovies.add(new_movie)
    st.sidebar.success("Película agregada correctamente")
