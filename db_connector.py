from sqlalchemy import create_engine, text
import pandas as pd
import json
import os

def load_db_config(filename="db_config.json"):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, filename)

    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            return json.load(f)
    else:
        raise FileNotFoundError(f"Config file not found at: {config_path}")
    
def create_mysql_engine(config_path="db_config.json"):
    cfg = load_db_config(config_path)
    user = cfg["user"]
    password = cfg["password"]
    host = cfg["host"]
    database = cfg["database"]
    port = cfg.get("port", 3306)

    connection_str = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
    return create_engine(connection_str)

def fetch_data_from_mysql(query, params=None, config_path="db_config.json"):
    try:
        engine = create_mysql_engine(config_path)
        with engine.connect() as conn:
            df = pd.read_sql(text(query), conn, params=params)
        return df
    except  Exception as e:
        print(f"Database error: {e}")
        return pd.DataFrame()
    
def get_distinct_values(column, table="mix_summary", config_path="db_config.json"):
    try:
        engine = create_mysql_engine(config_path)
        query = f"SELECT DISTINCT {column} FROM {table}"
        df = pd.read_sql(query, engine)
        return [row[column] for index, row in df.iterrows() if row[column] not in [None, ""]]
    except Exception as e:
        print(f"Error getting distinct values from {column}: {e}")
        return []