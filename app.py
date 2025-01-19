from flask import Flask, jsonify, request, redirect, Response
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

BASE_URL = "https://q1n.net/"

@app.route('/api/episodes', methods=['GET'])
def episodes_api():
    url = f"{BASE_URL}e/"
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    
    if response.status_code != 200:
        return jsonify({"error": f"Não foi possível obter os episódios. Status Code: {response.status_code}, Response: {response.text}"}), 500

    soup = BeautifulSoup(response.text, 'html.parser')
    episodes = []
    
    content = soup.find('div', class_='content right full')
    if content:
        archive = content.find('div', id='archive-content')
        if archive:
            for episode in archive.find_all('article', class_='item se episodes')[:10]:  # Limite de 10 itens
                title = episode.find('h3').text.strip()
                episode_url = episode.find('a')['href']
                img_tag = episode.find('img')
                img_url = img_tag['src'] if img_tag else None

                quality = episode.find('span', class_='quality').text.strip() if episode.find('span', class_='quality') else 'N/A'

                proxy_img_url = f"{request.url_root}image/{img_url.replace(BASE_URL, '')}" if img_url else None
                proxy_episode_url = f"{request.url_root}{episode_url.replace(BASE_URL, '')}"

                episodes.append({
                    'title': title,
                    'url': proxy_episode_url,
                    'image': proxy_img_url,
                    'quality': quality
                })

    return jsonify(episodes)

@app.route('/episodio/<path:episode_path>')
def episode_proxy(episode_path):
    original_url = f"{BASE_URL}e/{episode_path}"
    response = requests.get(original_url, headers={'User-Agent': 'Mozilla/5.0'})

    if response.status_code == 200:
        return redirect(original_url)
    else:
        return "Episódio não encontrado", 404

@app.route('/image/<path:image_path>')
def image_proxy(image_path):
    original_url = f"{BASE_URL}e/{image_path}"
    response = requests.get(original_url, headers={'User-Agent': 'Mozilla/5.0'})

    if response.status_code != 200:
        return jsonify({"error": "Imagem não encontrada."}), 404

    return Response(response.content, content_type=response.headers.get('Content-Type', 'image/jpeg'))

if __name__ == '__main__':
    app.run(debug=True)
    
