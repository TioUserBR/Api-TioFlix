from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

# URLs das APIs externas
URL_ANIMES = "https://raw.githubusercontent.com/CORINGA88hacker/api-animes/refs/heads/main/animes.json"
URL_EPISODIOS = "https://raw.githubusercontent.com/CORINGA88hacker/api-animes/refs/heads/main/episodios.json"
URL_TEMPORADAS = "https://raw.githubusercontent.com/CORINGA88hacker/api-animes/refs/heads/main/temporadas.json"


def get_json_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"erro": str(e)}


@app.route("/Api/animes/", methods=["GET"])
def api_animes():
    data = get_json_from_url(URL_ANIMES)
    return jsonify(data)


@app.route("/Api/episodios/", methods=["GET"])
def api_episodios():
    data = get_json_from_url(URL_EPISODIOS)
    return jsonify(data)


@app.route("/Api/temporadas/", methods=["GET"])
def api_temporadas():
    data = get_json_from_url(URL_TEMPORADAS)
    return jsonify(data)


@app.route("/Api/pesquisa", methods=["GET"])
def api_pesquisa():
    nome = request.args.get("nome")  # parâmetro ?nome=
    if not nome:
        return jsonify({"erro": "Parâmetro 'nome' é obrigatório"}), 400

    data = get_json_from_url(URL_ANIMES)

    if isinstance(data, dict) and "erro" in data:
        return jsonify(data), 500

    # Pesquisa ignorando maiúsculas/minúsculas
    resultados = [anime for anime in data if nome.lower() in anime.get("nome", "").lower()]

    if resultados:
        return jsonify(resultados)
    else:
        return jsonify({"mensagem": f"Nenhum anime encontrado com nome contendo '{nome}'"}), 404


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
