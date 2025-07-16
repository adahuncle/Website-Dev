from flask import request, jsonify
import pandas as pd
import mysql.connector
import uuid
from config import load_db_config
from . import plot_bp
from plot_mixer_data import plot_all_signals_html

db_config = load_db_config()

@plot_bp.route("/api/prepare-plot", methods=["POST"])
def prepare_plot():
    from cache import plot_cache
    req_data = request.get_json()
    if not req_data or "batches" not in req_data:
        print("⚠️ Bad request. Body:", req_data)
        return jsonify({"error": "No data provided"}), 400

    data = req_data["batches"]
    plot_id = str(uuid.uuid4())
    plot_cache[plot_id] = data
    return jsonify({"plot_id": plot_id})


@plot_bp.route("/plot/<plot_id>")
def display_plot(plot_id):
    from cache import plot_cache

    data = plot_cache.get(plot_id)
    if not data:
        return "Plot data not found", 404

    summary_ids = [row["id"] for row in data]

    # Fetch detail and summary data
    detail_query = """
    SELECT d.*, s.batch, s.program, s.date
    FROM mix_detail d
    JOIN mix_summary s ON d.id_summary = s.id
    WHERE d.id_summary IN ({})
    """.format(','.join(['%s'] * len(summary_ids)))

    import mysql.connector
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute(detail_query, summary_ids)
    df = pd.DataFrame(cursor.fetchall())
    cursor.close()
    conn.close()

    print(f"🔍 Data passed to plot (len={len(data)}):", data)
    print(f"📊 Summary IDs: {summary_ids}")
    print("🧪 DF Preview (post join):")
    print(df.head())


    # Generate HTML version of plot
    fig_html = plot_all_signals_html(df)
    return f"<html><body>{fig_html}</body></html>"

