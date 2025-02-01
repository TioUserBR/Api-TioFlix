import requests
from flask import Flask, Response

app = Flask(__name__)

# Cabeçalhos adicionais para tentar contornar o bloqueio
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; U; Android 15; pt; 23129RA5FL Build/AQ3A.240829.003) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/110.0.0.0 Mobile Safari/537.36",
    "Referer": "https://animefire.plus/",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "Connection": "keep-alive",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
}

BASE_URL = "https://animefire.plus"

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def proxy(path):
    url = f"{BASE_URL}/{path}"
    try:
        # Faz a requisição ao site original com os cabeçalhos modificados
        response = requests.get(url, headers=HEADERS, stream=True)

        # Retorna o conteúdo para o cliente mantendo o status e headers
        return Response(response.iter_content(chunk_size=8192), status=response.status_code, content_type=response.headers['Content-Type'])

    except requests.exceptions.RequestException as e:
        return f"Erro ao acessar {BASE_URL}: {e}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
