import os
import streamlit as st
import pandas as pd
import requests
import cloudpickle
from api.s3_downloader import S3Downloader 

def download_files_if_needed():
    s3_downloader = S3Downloader()

    model_path = os.path.join('models', 'game_recommender.pkl')
    games_path = os.path.join('data', 'games.csv')

    if not os.path.exists(model_path):
        st.write("Baixando modelo do S3...")
        s3_downloader.download_model()

    if not os.path.exists(games_path):
        st.write("Baixando games.csv do S3...")
        s3_downloader.download_csv()

# Função para carregar o modelo
@st.cache_resource
def load_model():
    model_path = os.path.join('models', 'game_recommender.pkl')
    with open(model_path, 'rb') as f:
        model = cloudpickle.load(f)
    return model

# Função para carregar o CSV
@st.cache_data
def load_games_data():
    csv_path = os.path.join('data', 'games.csv')
    return pd.read_csv(csv_path)

# Função para carregar o CSS de um arquivo externo
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Função para buscar o poster do jogo usando a API da Steam via app_id
def fetch_game_poster(app_id):
    url = f"https://store.steampowered.com/api/appdetails?appids={app_id}"
    response = requests.get(url)
    data = response.json()

    if str(app_id) in data and data[str(app_id)]['success']:
        game_data = data[str(app_id)]['data']
        if 'header_image' in game_data:
            return game_data['header_image']
        else:
            return "Imagem não disponível"
    else:
        return "Imagem não disponível"

download_files_if_needed()

# Carregar o arquivo CSS externo
load_css(os.path.join("static", "style.css"))

# Carregar o modelo de recomendação
recommender = load_model()

# Carregar a lista de jogos
games = load_games_data()
games_list = games['title'].values

# Cabeçalho da aplicação
st.markdown('<h1 class="text-center text-danger">Game Recommender System</h1>', unsafe_allow_html=True)

# Dropdown para selecionar um jogo
selectvalue = st.selectbox("Selecione um jogo", games_list)

# Função para recomendar jogos
def recommend_games_by_app_id(app_id, n_recommendations=5):
    try:
        # Obter as recomendações do modelo usando o app_id
        recommendations_df = recommender.recommend_games(app_id=app_id, n_recommendations=n_recommendations)

        # Preparar listas para os títulos e os posters dos jogos recomendados
        recommended_games = recommendations_df['title'].values
        recommended_posters = [fetch_game_poster(game_id) for game_id in recommendations_df['app_id'].values]
        
        return recommended_games, recommended_posters
    except ValueError as e:
        st.error(f"Erro: {str(e)}")
        return [], []

# Obter o app_id baseado no título do jogo selecionado
selected_game_id = games[games['title'] == selectvalue]['app_id'].values[0]

# Botão para exibir recomendações
if st.button("Exibir Recomendações"):
    recommended_titles, recommended_posters = recommend_games_by_app_id(selected_game_id)

    if len(recommended_titles) > 0 and len(recommended_posters) > 0:
        rows = len(recommended_titles) // 3 + (len(recommended_titles) % 3 > 0)

        for row in range(rows):
            cols = st.columns(3)  # Cria 3 colunas horizontais

            for i in range(3):
                index = row * 3 + i
                if index < len(recommended_titles):
                    with cols[i]:
                        st.markdown(f"""
                        <div class="card-container">
                            <img src="{recommended_posters[index]}" class="img-fluid" alt="{recommended_titles[index]}">
                            <p class="text-center mt-2">{recommended_titles[index]}</p>
                        </div>
                        """, unsafe_allow_html=True)
