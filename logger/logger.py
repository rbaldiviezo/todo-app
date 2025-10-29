from flask import Flask, request, jsonify
import os, datetime

app = Flask(__name__)

LOG_PATH = "/logs/service.log"
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

@app.route("/log", methods=["POST"])
def write_log():
    data = request.get_json()
    msg = data.get("message", "Evento sin mensaje")
    with open(LOG_PATH, "a") as f:
        f.write(f"[{datetime.datetime.now()}] {msg}\n")
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000)
