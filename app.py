from flask import Flask, jsonify, request, redirect, Response
import cfscrape
from bs4 import BeautifulSoup
from urllib.parse import quote  # Substituído aqui

app = Flask(__name__)

scraper = cfscrape.create_scraper()

@app.route('/api/episodes', methods=['GET'])
def episodes_api():
    url = "https://animesonlinecc.to/episodio/"
    try:
        response = scraper.get(url)
        response.raise_for_status()  # Levanta um erro se o status não for 200
    except Exception as e:
        return jsonify({"error": f"Erro ao obter os episódios: {str(e)}"}), 500

    soup = BeautifulSoup(response.text, 'html.parser')
    episodes = []
    
    for episode in soup.find_all('article', class_='item se episodes')[:10]:
        title = episode.find('h3').text.strip()
        episode_url = episode.find('a')['href']
        img_url = episode.find('img')['src']

        img_url = img_url.replace("https://animesonlinecc.to/", "")
        proxy_img_url = f"{request.url_root}image/{quote(img_url)}"

        episode_url = episode_url.replace("https://animesonlinecc.to/", "")
        proxy_episode_url = f"{request.url_root}{quote(episode_url)}"

        episodes.append({
            'title': title,
            'url': proxy_episode_url,
            'image': proxy_img_url
        })

    return jsonify(episodes)

@app.route('/episodio/<path:episode_path>')
def episode_proxy(episode_path):
    original_url = f"https://animesonlinecc.to/{episode_path}"
    try:
        response = scraper.get(original_url)
        response.raise_for_status()
    except Exception as e:
        return jsonify({"error": f"Erro ao acessar o episódio: {str(e)}"}), 500

    if response.status_code == 200:
        return redirect(original_url)
    else:
        return jsonify({"error": "Episódio não encontrado"}), 404

@app.route('/image/<path:image_path>')
def image_proxy(image_path):
    original_url = f"https://animesonlinecc.to/{image_path}"
    try:
        response = scraper.get(original_url)
        response.raise_for_status()
    except Exception as e:
        return jsonify({"error": f"Erro ao acessar a imagem: {str(e)}"}), 500

    if response.status_code != 200:
        return jsonify({"error": "Imagem não encontrada."}), 404
    
    return Response(response.content, content_type=response.headers.get('Content-Type', 'image/jpeg'))

if __name__ == '__main__':
    app.run(debug=True)
    
