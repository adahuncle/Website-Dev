from flask import request, jsonify
import mysql.connector
from decimal import Decimal
import datetime
from config import load_db_config
from . import search_bp

db_config = load_db_config()

@search_bp.route("/api/search", methods=["POST"])
def search_batches():
    data = request.json
    compounds = data.get("compounds", [])
    dt_reasons = data.get("dt_reasons", [])
    start_date = data.get("start_date")
    end_date = data.get("end_date")
    batch = data.get("batch", [])

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM mix_summary WHERE 1=1"
    params = []

    if compounds:
        query += f" AND program IN ({','.join(['%s'] * len(compounds))})"
        params.extend(compounds)
    if dt_reasons:
        query += f" AND dt_reason IN ({','.join(['%s'] * len(dt_reasons))})"
        params.extend(dt_reasons)
    if start_date and end_date:
        query += " AND date BETWEEN %s AND %s"
        params.extend([start_date, end_date])
    elif start_date:
        query += " AND date >= %s"
        params.append(start_date)
    elif end_date:
        query += " AND date <= %s"
        params.append(end_date)
    if batch:
        batch_like_clauses = " OR ".join(["batch LIKE %s" for _ in batch])
        query += f" AND ({batch_like_clauses})"
        params.extend([f"%{bid}%" for bid in batch])


    cursor.execute(query, params)
    results = cursor.fetchall()
    cursor.close()
    conn.close()

    for row in results:
        for key, value in row.items():
            if isinstance(value, (datetime.date, datetime.datetime)):
                row[key] = value.strftime("%Y-%m-%d")
            elif isinstance(value, datetime.timedelta):
                row[key] = str(value)
            elif isinstance(value, Decimal):
                row[key] = float(value)
            elif value is None:
                row[key] = ""

    return jsonify(results)
