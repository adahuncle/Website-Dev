from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import mysql.connector
import json
import os
import datetime

app = Flask(__name__, static_url_path='/static', static_folder='static', template_folder='templates')
CORS(app)  # Enables Cross-Origin requests (important for frontend JS)

def load_db_config(path="db_config.json"):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_dir, path)

    if os.path.exists(full_path):
        with open(full_path, "r") as f:
            return json.load(f)
    else:
        raise FileNotFoundError(f"Database config file not found at {full_path}")

db_config = load_db_config()

# === Home route for HTML ===
@app.route("/")
def index():
    return render_template("index.html")


# === Compounds endpoint for Select2 ===
@app.route("/api/compounds")
def get_compounds():
    search_term = request.args.get("q", "").lower()
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    if search_term:
        cursor.execute("SELECT DISTINCT program FROM mix_summary WHERE program LIKE %s", (f"%{search_term}%",))
    else:
        cursor.execute("SELECT DISTINCT program FROM mix_summary")

    compounds = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return jsonify(compounds)

# === Downtime reasons endpoint for Select2 ===
@app.route("/api/dt-reason")
def get_dt_reasons():
    search_term = request.args.get("q", "").lower()
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    if search_term:
        cursor.execute("SELECT DISTINCT dt_reason FROM mix_summary WHERE dt_reason LIKE %s", (f"%{search_term}%",))
    else:
        cursor.execute("SELECT DISTINCT dt_reason FROM mix_summary")

    reasons = [row[0] for row in cursor.fetchall() if row[0]]  # Filter out null/None
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

    # Apply date range filtering (optional start and/or end)
    if start_date and not end_date:
        query += " AND date >= %s"
        params.append(start_date)
    elif end_date and not start_date:
        query += " AND date <= %s"
        params.append(end_date)
    elif start_date and end_date:
        query += " AND date BETWEEN %s AND %s"
        params.extend([start_date, end_date])

    if batch_ids:
        query += " AND batch_id LIKE %s"
        params.append(f"%{batch_ids}%")

    print("Start date:", start_date)
    print("End date:", end_date)


    cursor.execute(query, params)
    results = cursor.fetchall()
    cursor.close()
    conn.close()

    from decimal import Decimal

    for row in results:
        for key, value in row.items():
            if isinstance(value, (datetime.date, datetime.datetime)):
                row[key] = value.strftime("%Y-%m-%d")  # or "%m/%d/%Y" if preferred
            elif isinstance(value, datetime.timedelta):
                row[key] = str(value)
            elif isinstance(value, Decimal):
                row[key] = float(value)
            elif value is None:
                row[key] = ""  # Avoid sending None as undefined/null in JS


    print("Sample row:", results[0] if results else "No results")

    return jsonify(results)


if __name__ == "__main__":
    app.run(debug=True)
