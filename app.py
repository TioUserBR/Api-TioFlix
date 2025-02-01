from flask import Flask, Response, request
import cloudscraper

app = Flask(__name__)

# Cria um scraper com configuração de navegador mobile e Android
scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'chrome',
        'platform': 'android',
        'mobile': True
    }
)

BASE_URL = "https://animefire.plus"

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def proxy(path):
    # Monta a URL destino
    url = f"{BASE_URL}/{path}"
    try:
        # Realiza a requisição utilizando o cloudscraper
        response = scraper.get(url, stream=True)
        
        # Repassa os dados para o cliente, mantendo status e content-type
        return Response(
            response.iter_content(chunk_size=8192),
            status=response.status_code,
            content_type=response.headers.get('Content-Type')
        )
    except Exception as e:
        return f"Erro ao acessar {BASE_URL}: {e}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
