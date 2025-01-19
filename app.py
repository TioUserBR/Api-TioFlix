from flask import Flask, jsonify, request, redirect, Response
import requests
from bs4 import BeautifulSoup
import json

app = Flask(__name__)

# URL do FlareSolverr, altere para a URL onde o FlareSolverr está rodando
FLARE_SOLVERR_URL = "https://api-animes-free.vercel.app/v1"

def flare_solverr_request(url):
    """Função que usa FlareSolverr para resolver o Cloudflare"""
    data = {
        "cmd": "request.get",
        "url": url,
        "max_timeout": 60000  # tempo máximo de espera
    }
    
    response = requests.post(FLARE_SOLVERR_URL, json=data)
    if response.status_code == 200:
        result = response.json()
        if "solution" in result:
            return result["solution"]["url"]
    return None

@app.route('/api/episodes', methods=['GET'])
def episodes_api():
    url = "https://animesonlinecc.to/episodio/"
    
    # Usando o FlareSolverr para obter a URL que contorna o Cloudflare
    solved_url = flare_solverr_request(url)
    
    if solved_url is None:
        return jsonify({"error": "Não foi possível contornar o Cloudflare."}), 500

    # Pegando o conteúdo da página após contornar o Cloudflare
    response = requests.get(solved_url)
    if response.status_code != 200:
        return jsonify({"error": "Não foi possível obter os episódios."}), 500

    soup = BeautifulSoup(response.text, 'html.parser')
    episodes = []

    # Limite de 10 episódios
    for episode in soup.find_all('article', class_='item se episodes')[:10]:
        title = episode.find('h3').text.strip()
        episode_url = episode.find('a')['href']
        img_url = episode.find('img')['src']

        img_url = img_url.replace("https://animesonlinecc.to/", "")
        proxy_img_url = f"{request.url_root}image/{img_url}"

        episode_url = episode_url.replace("https://animesonlinecc.to/", "")
        proxy_episode_url = f"{request.url_root}{episode_url}"

        episodes.append({
            'title': title,
            'url': proxy_episode_url,
            'image': proxy_img_url
        })

    return jsonify(episodes)

@app.route('/episodio/<path:episode_path>')
def episode_proxy(episode_path):
    original_url = f"https://animesonlinecc.to/{episode_path}"
    
    # Usando FlareSolverr para obter a URL contornada
    solved_url = flare_solverr_request(original_url)
    
    if solved_url is None:
        return jsonify({"error": "Não foi possível contornar o Cloudflare."}), 500

    response = requests.get(solved_url)
    if response.status_code == 200:
        return redirect(original_url)
    else:
        return jsonify({"error": "Episódio não encontrado"}), 404

@app.route('/image/<path:image_path>')
def image_proxy(image_path):
    original_url = f"https://animesonlinecc.to/{image_path}"
    
    # Usando FlareSolverr para obter a URL contornada
    solved_url = flare_solverr_request(original_url)
    
    if solved_url is None:
        return jsonify({"error": "Não foi possível contornar o Cloudflare."}), 500

    response = requests.get(solved_url)
    if response.status_code != 200:
        return jsonify({"error": "Imagem não encontrada."}), 404
    
    return Response(response.content, content_type=response.headers.get('Content-Type', 'image/jpeg'))

if __name__ == '__main__':
    app.run(debug=True)
    
