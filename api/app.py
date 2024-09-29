import streamlit as st
import pandas as pd
import requests
import cloudpickle

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

# Carregar o arquivo CSS externo
load_css("../static/style.css")

# Carregar o modelo de recomendação
with open('../data/game_recommender.pkl', 'rb') as f:
    recommender = cloudpickle.load(f)

# Carregar a lista de jogos
games = pd.read_csv("../data/games.csv")
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
