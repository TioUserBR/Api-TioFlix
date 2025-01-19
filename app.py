from flask import Flask, jsonify, request, redirect, Response
import cfscrape
from bs4 import BeautifulSoup
from urllib.parse import quote  # Para codificar a URL corretamente

app = Flask(__name__)

# Cria um objeto de scraper
scraper = cfscrape.create_scraper()

@app.route('/api/episodes', methods=['GET'])
def episodes_api():
    url = "https://animesonlinecc.to/episodio/"
    response = scraper.get(url)  # Usando cfscrape para contornar o Cloudflare

    if response.status_code != 200:
        return jsonify({"error": "Não foi possível obter os episódios."}), 500

    soup = BeautifulSoup(response.text, 'html.parser')
    episodes = []
    
    # Limitar a 10 episódios
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
    response = scraper.get(original_url)  # Usando cfscrape aqui também
    
    # Verifica se o episódio existe
    if response.status_code == 200:
        return redirect(original_url)
    else:
        return "Episódio não encontrado", 404

@app.route('/image/<path:image_path>')
def image_proxy(image_path):
    original_url = f"https://animesonlinecc.to/{image_path}"
    response = scraper.get(original_url)  # Usando cfscrape aqui também
    
    # Verifica se a imagem existe
    if response.status_code != 200:
        return jsonify({"error": "Imagem não encontrada."}), 404
    
    return Response(response.content, content_type=response.headers.get('Content-Type', 'image/jpeg'))

if __name__ == '__main__':
    app.run(debug=True)
    
