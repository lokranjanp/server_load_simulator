from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# List of backend server URLs
backend_servers = [
    "http://localhost:7019",
    "http://localhost:7020",
    "http://localhost:7021"
]

index = 0


@app.route("/api/<path:path>", methods=["GET", "POST"])
def load_balance(path):
    global index
    server = backend_servers[index]
    index = (index + 1) % len(backend_servers)

    try:
        if request.method == "POST":
            response = requests.post(f"{server}/api/{path}", json=request.get_json())
        else:
            response = requests.get(f"{server}/api/{path}", params=request.args)

        return jsonify(response.json()), response.status_code
    except Exception as e:
        return {"error": str(e)}, 500


if __name__ == "__main__":
    app.run(port=8000)
