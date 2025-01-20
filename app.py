from flask import Flask, jsonify, request, Response
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

BASE_URL = "https://q1n.net/"
HEADERS = {'User-Agent': 'Mozilla/5.0'}

@app.route('/api/newEpList', methods=['GET'])
def episodes_api():
    url = f"{BASE_URL}e/"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code != 200:
        return jsonify({"error": f"Não foi possível obter os episódios. Status Code: {response.status_code}, Response: {response.text}"}), 500

    soup = BeautifulSoup(response.text, 'html.parser')
    episodes = []
    
    content = soup.find('div', class_='content right full')
    if content:
        archive = content.find('div', id='archive-content')
        if archive:
            for episode in archive.find_all('article', class_='item se episodes')[:50]:  # Limite de 10 itens
                title = episode.find('h3').text.strip()
                episode_url = episode.find('a')['href']
                img_tag = episode.find('img')
                img_url = img_tag['src'] if img_tag else None
                img_alt = img_tag['alt'] if img_tag and 'alt' in img_tag.attrs else None

                quality = episode.find('span', class_='quality').text.strip() if episode.find('span', class_='quality') else 'N/A'

                proxy_img_url = f"{request.url_root}image/{img_url.replace(BASE_URL, '')}" if img_url else None
                proxy_episode_url = f"{request.url_root}{episode_url.replace(BASE_URL, '')}"

                episodes.append({
                    'title': title,
                    'name': img_alt,
                    'url': proxy_episode_url,
                    'image': proxy_img_url,
                    'quality': quality
                })

    return jsonify(episodes)

@app.route('/e/<path:episode_path>', methods=['GET'])
def episode_details(episode_path):
    original_url = f"{BASE_URL}e/{episode_path}"
    response = requests.get(original_url, headers=HEADERS)

    if response.status_code != 200:
        return jsonify({"error": "Episódio não encontrado."}), 404

    soup = BeautifulSoup(response.text, 'html.parser')

    # Extrair gêneros
    genres_div = soup.find('div', class_='sgeneros')
    genres = [a.text.strip() for a in genres_div.find_all('a')] if genres_div else []

    # Extrair imagem do poster
    poster_img = None
    poster_div = soup.find('div', class_='poster')
    if poster_div and poster_div.find('img'):
        poster_img = poster_div.find('img')['src']

    # Extrair título
    title = soup.find('span', id='titleHis').text.strip() if soup.find('span', id='titleHis') else None

    # Extrair thumb
    thumb = soup.find('span', id='thumbHis')['data-src'] if soup.find('span', id='thumbHis') else None

    # Extrair sinopse
    synopsis_div = soup.find('div', class_='synopsis')
    synopsis = synopsis_div.text.strip() if synopsis_div else None

    # Retornar os dados no formato JSON
    return jsonify({
        "title": title,
        "image": poster_img,
        "thumb": thumb,
        "genres": genres,
        "synopsis": synopsis
    })

@app.route('/calendario', methods=['GET'])
def calendario():
    url = f"{BASE_URL}calendario/"
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})

    if response.status_code != 200:
        return jsonify({"error": f"Não foi possível obter os dados do calendário. Status Code: {response.status_code}, Response: {response.text}"}), 500

    soup = BeautifulSoup(response.text, 'html.parser')
    shows = []

    # Processar os elementos do calendário
    for item in soup.find_all('article', class_='item tvshows'):
        title = item.find('h3').text.strip() if item.find('h3') else None
        year = item.find('span').text.strip() if item.find('span') else None

        img_tag = item.find('img')
        img_url = img_tag['src'] if img_tag else None
        img_alt = img_tag['alt'] if img_tag and 'alt' in img_tag.attrs else None
        show_url = item.find('a')['href'] if item.find('a') else None

        # Criar links camuflados
        proxy_img_url = f"{request.url_root}image/{img_url.replace(BASE_URL, '')}" if img_url else None
        proxy_show_url = f"{request.url_root}show/{show_url.replace(BASE_URL, '')}" if show_url else None

        shows.append({
            "title": title,
            "alt": img_alt,
            "image": proxy_img_url,
            "url": proxy_show_url,
            "year": year
        })

    return jsonify(shows)

@app.route('/show/<path:show_path>', methods=['GET'])
def show_proxy(show_path):
    original_url = f"{BASE_URL}{show_path}"
    response = requests.get(original_url, headers={'User-Agent': 'Mozilla/5.0'})

    if response.status_code != 200:
        return jsonify({"error": "Conteúdo não encontrado."}), 404

    return Response(response.content, content_type=response.headers.get('Content-Type'))


@app.route('/image/<path:image_path>')
def image_proxy(image_path):
    original_url = f"{BASE_URL}{image_path}"
    response = requests.get(original_url, headers=HEADERS)

    if response.status_code != 200:
        return jsonify({"error": "Imagem não encontrada."}), 404

    content_type = response.headers.get('Content-Type', 'image/jpeg')  # Default para 'image/jpeg'
    return Response(response.content, content_type=content_type)

if __name__ == '__main__':
    app.run(debug=True)
     
