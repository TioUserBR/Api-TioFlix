from flask import Flask, request, Response
import cloudscraper

app = Flask(__name__)

# Cria um scraper configurado para simular um navegador mobile Android
scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'chrome',
        'platform': 'android',
        'mobile': True
    }
)

BASE_URL = "https://animefire.plus"

def make_request(method, url, **kwargs):
    """Função auxiliar para executar a requisição com o cloudscraper."""
    try:
        return scraper.request(method, url, **kwargs)
    except Exception as e:
        raise e

@app.route("/", defaults={"path": ""}, methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
@app.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
def proxy(path):
    # Monta a URL de destino incluindo a rota passada
    url = f"{BASE_URL}/{path}"
    
    # Captura os parâmetros da query string
    params = request.args.to_dict()

    # Repassa cabeçalhos relevantes, removendo cabeçalhos que possam causar conflito (ex: 'Host')
    headers = {key: value for key, value in request.headers if key.lower() != "host"}
    
    # Garante o User-Agent desejado (caso o site verifique esse cabeçalho)
    headers["User-Agent"] = (
        "Mozilla/5.0 (Linux; U; Android 15; pt; 23129RA5FL Build/AQ3A.240829.003) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/110.0.0.0 Mobile Safari/537.36"
    )
    
    # Captura o corpo da requisição se for método que utiliza dados (POST, PUT, PATCH)
    data = request.get_data() if request.method in ["POST", "PUT", "PATCH"] else None

    try:
        # Realiza a requisição usando o cloudscraper
        response = make_request(
            request.method,
            url,
            params=params,
            headers=headers,
            data=data,
            stream=True
        )
        
        # Exclui cabeçalhos que podem interferir na resposta
        excluded_headers = ["content-encoding", "content-length", "transfer-encoding", "connection"]
        response_headers = [
            (name, value) for name, value in response.raw.headers.items() if name.lower() not in excluded_headers
        ]
        
        return Response(
            response.iter_content(chunk_size=8192),
            status=response.status_code,
            headers=response_headers
        )
    
    except Exception as e:
        return f"Erro ao acessar {url}: {e}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
