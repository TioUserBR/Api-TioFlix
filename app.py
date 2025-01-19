from flask import Flask, jsonify, request, redirect, Response
import requests
from bs4 import BeautifulSoup
import random

app = Flask(__name__)

# Lista de User-Agents
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edge/91.0.864.64',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:40.0) Gecko/20100101 Firefox/40.0',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
]

@app.route('/api/episodes', methods=['GET'])
def episodes_api():
    url = "https://animesonlinecc.to/episodio/"
    
    # Seleciona aleatoriamente um User-Agent da lista
    headers = {
        'User-Agent': random.choice(user_agents)
    }
    
    # Realiza a requisição com cabeçalho de User-Agent
    response = requests.get(url, headers=headers)

    # Imprime a resposta para depuração
    print(f"Status Code: {response.status_code}")
    print(f"Response Text: {response.text[:500]}")  # Apenas os primeiros 500 caracteres para verificar

    # Se a resposta não for 200 (OK), retorna erro
    if response.status_code != 200:
        return jsonify({"error": "Não foi possível obter os episódios."}), 500

    # Parsing do conteúdo HTML com BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Lista para armazenar os episódios
    episodes = []
    for episode in soup.find_all('article', class_='item se episodes'):
        title = episode.find('h3').text.strip()
        episode_url = episode.find('a')['href']
        img_url = episode.find('img')['src']

        # Substituindo a URL original da imagem e do episódio pela URL do proxy
        img_url = img_url.replace("https://animesonlinecc.to/", "")
        proxy_img_url = f"{request.url_root}image/{img_url}"

        episode_url = episode_url.replace("https://animesonlinecc.to/", "")
        proxy_episode_url = f"{request.url_root}{episode_url}"

        # Adicionando as informações no formato JSON
        episodes.append({
            'title': title,
            'url': proxy_episode_url,
            'image': proxy_img_url
        })

    # Retorna a lista de episódios em formato JSON
    return jsonify(episodes)

@app.route('/episodio/<path:episode_path>')
def episode_proxy(episode_path):
    # URL original do episódio
    original_url = f"https://animesonlinecc.to/{episode_path}"
    
    # Seleciona aleatoriamente um User-Agent da lista
    headers = {
        'User-Agent': random.choice(user_agents)
    }
    
    # Realiza a requisição para o episódio com cabeçalho de User-Agent
    response = requests.get(original_url, headers=headers)
    
    # Verifica se o episódio foi encontrado
    if response.status_code == 200:
        return redirect(original_url)
    else:
        return "Episódio não encontrado", 404

@app.route('/image/<path:image_path>')
def image_proxy(image_path):
    # URL original da imagem
    original_url = f"https://animesonlinecc.to/{image_path}"
    
    # Seleciona aleatoriamente um User-Agent da lista
    headers = {
        'User-Agent': random.choice(user_agents)
    }
    
    # Realiza a requisição para a imagem com cabeçalho de User-Agent
    response = requests.get(original_url, headers=headers)
    
    # Verifica se a imagem foi encontrada
    if response.status_code != 200:
        return jsonify({"error": "Imagem não encontrada."}), 404
    
    # Retorna a imagem com o tipo de conteúdo correto
    return Response(response.content, content_type=response.headers.get('Content-Type', 'image/jpeg'))

if __name__ == '__main__':
    app.run(debug=True)
    
