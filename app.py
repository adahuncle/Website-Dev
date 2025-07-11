from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import mysql.connector

app = Flask(__name__, static_url_path='', static_folder='.', template_folder='.')
CORS(app)  # Enables Cross-Origin requests (important for frontend JS)

# === DB CONFIG ===
db_config = {
    "host": "localhost",
    "user": "your_username",
    "password": "your_password",
    "database": "your_db_name"
}

# === Home route for HTML ===
@app.route("/")
def index():
    return render_template("index.html")


# === Compounds endpoint for Select2 ===
@app.route("/api/compounds")
def get_compounds():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT program FROM mix_summary")
    compounds = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return jsonify(compounds)


# === Downtime reasons endpoint for Select2 ===
@app.route("/api/dt-reason")
def get_dt_reasons():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT dt_reason FROM mix_summary")
    reasons = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return jsonify(reasons)


# === Search/filter endpoint ===
@app.route("/api/search", methods=["POST"])
def search_batches():
    data = request.json  # JSON from JS
    compounds = data.get("compounds", [])
    dt_reasons = data.get("dt_reasons", [])
    start_date = data.get("start_date")
    end_date = data.get("end_date")
    batch_ids = data.get("batch_ids", "")

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    # Start building query
    query = "SELECT * FROM mix_summary WHERE 1=1"
    params = []

    if compounds:
        placeholders = ','.join(['%s'] * len(compounds))
        query += f" AND program IN ({placeholders})"
        params.extend(compounds)

    if dt_reasons:
        placeholders = ','.join(['%s'] * len(dt_reasons))
        query += f" AND dt_reason IN ({placeholders})"
        params.extend(dt_reasons)

    if start_date:
        query += " AND date >= %s"
        params.append(start_date)

    if end_date:
        query += " AND date <= %s"
        params.append(end_date)

    if batch_ids:
        query += " AND batch_id LIKE %s"
        params.append(f"%{batch_ids}%")

    cursor.execute(query, params)
    results = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify(results)


if __name__ == "__main__":
    app.run(debug=True)
