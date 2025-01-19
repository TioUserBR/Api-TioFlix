from flask import Flask, jsonify, request, redirect, Response
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Cabeçalho com o User-Agent para simular um navegador
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
}

@app.route('/api/episodes', methods=['GET'])
def episodes_api():
    url = "https://animesonlinecc.to/episodio/"
    response = requests.get(url, headers=headers)

    # Imprima a resposta para depuração
    print(f"Status Code: {response.status_code}")
    print(f"Response Text: {response.text[:500]}")  # Apenas os primeiros 500 caracteres

    if response.status_code != 200:
        return jsonify({"error": "Não foi possível obter os episódios."}), 500

    soup = BeautifulSoup(response.text, 'html.parser')
    episodes = []
    for episode in soup.find_all('article', class_='item se episodes'):
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
    response = requests.get(original_url, headers=headers)
    
    # Verifica se o episódio existe
    if response.status_code == 200:
        return redirect(original_url)
    else:
        return "Episódio não encontrado", 404

@app.route('/image/<path:image_path>')
def image_proxy(image_path):
    original_url = f"https://animesonlinecc.to/{image_path}"
    response = requests.get(original_url, headers=headers)
    
    # Verifica se a imagem existe
    if response.status_code != 200:
        return jsonify({"error": "Imagem não encontrada."}), 404
    
    return Response(response.content, content_type=response.headers.get('Content-Type', 'image/jpeg'))

if __name__ == '__main__':
    app.run(debug=True)
    
