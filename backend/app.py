from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
import os, time, requests

app = Flask(__name__)
CORS(app)

DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("POSTGRES_DB", "todo_db")
DB_USER = os.getenv("POSTGRES_USER", "todo_user")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "todo_pass")
LOGGER_URL = os.getenv("LOGGER_URL", "http://logger:4000/log")

def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            task TEXT NOT NULL
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

@app.route("/tasks", methods=["GET"])
def get_tasks():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, task FROM tasks ORDER BY id;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([{"id": r[0], "task": r[1]} for r in rows])

@app.route("/tasks", methods=["POST"])
def add_task():
    data = request.get_json()
    task = data.get("task")
    if not task:
        return jsonify({"error": "Falta el campo 'task'"}), 400

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO tasks (task) VALUES (%s);", (task,))
    conn.commit()
    cur.close()
    conn.close()

    send_log(f"Tarea agregada: {task}")

    return jsonify({"message": "Tarea agregada"}), 201


def wait_for_db():
    for i in range(10):  # reintentar hasta 10 veces
        try:
            conn = get_connection()
            conn.close()
            print("✅ Conexión con DB exitosa")
            return
        except psycopg2.OperationalError as e:
            print(f"⏳ Esperando DB ({i+1}/10)...")
            time.sleep(3)
    print("❌ No se pudo conectar a la base de datos")
    exit(1)
    
def send_log(message):
    try:
        requests.post(LOGGER_URL, json={"message": message}, timeout=2)
    except Exception as e:
        print(f"[⚠️] No se pudo enviar log: {e}")

if __name__ == "__main__":
    wait_for_db()
    init_db()
    app.run(host="0.0.0.0", port=5000)
