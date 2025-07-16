from flask import request, jsonify
import mysql.connector
from config import load_db_config
from . import dropdown_bp

db_config = load_db_config()

@dropdown_bp.route("/api/compounds")
def get_compounds():
    search_term = request.args.get("q", "").lower()
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    if search_term:
        cursor.execute("SELECT DISTINCT program FROM mix_summary WHERE program LIKE %s", (f"%{search_term}%",))
    else:
        cursor.execute("SELECT DISTINCT program FROM mix_summary")
    data = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return jsonify(data)

@dropdown_bp.route("/api/dt-reason")
def get_dt_reasons():
    search_term = request.args.get("q", "").lower()
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    if search_term:
        cursor.execute("SELECT DISTINCT dt_reason FROM mix_summary WHERE dt_reason LIKE %s", (f"%{search_term}%",))
    else:
        cursor.execute("SELECT DISTINCT dt_reason FROM mix_summary")
    data = [row[0] for row in cursor.fetchall() if row[0]]
    cursor.close()
    conn.close()
    return jsonify(data)
