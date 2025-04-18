from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

backend_servers = {
    "S1": "http://localhost:7019",
    "S2": "http://localhost:7020",
    "S3": "http://localhost:7021"
}

def calculate_score(metrics):
    # Replace with ML-derived weights or custom logic
    cpu_weight = -0.4291
    mem_weight = -0.2001
    load_weight = -0.0966
    return (
        cpu_weight * (100 - metrics['cpu_percent']) +
        mem_weight * (100 - metrics['memory_percent']) +
        load_weight * (100 - metrics['load_avg'])
    )

@app.route("/api/<path:path>", methods=["GET", "POST"])
def smart_balance(path):
    scores = {}
    for sid, url in backend_servers.items():
        try:
            r = requests.get(f"{url}/metrics")
            if r.status_code == 200:
                metrics = r.json()
                score = calculate_score(metrics)
                scores[sid] = (score, url)
        except:
            continue

    if not scores:
        return {"error": "All servers unavailable"}, 503

    # Choose the server with the best score
    best_server = max(scores.items(), key=lambda x: x[1][0])[1][1]

    try:
        if request.method == "POST":
            response = requests.post(f"{best_server}/api/{path}", json=request.get_json())
        else:
            response = requests.get(f"{best_server}/api/{path}", params=request.args)

        return jsonify(response.json()), response.status_code
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == "__main__":
    app.run(port=8001)
