"""
dlt Ingestion Pipeline for VigilPay.
Loads raw CSV data into a DuckDB/BigQuery data warehouse table `raw_transactions`
under dataset `vigilpay_raw`, adding incremental load timestamps.
"""

import os
import sys
import pandas as pd
from datetime import datetime

# Import dlt if installed, otherwise provide robust wrapper for local duckdb loading
try:
    import dlt
    HAS_DLT = True
except ImportError:
    HAS_DLT = False

import duckdb

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
SAMPLE_CSV_PATH = os.path.join(DATA_DIR, "paysim_sample.csv")
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "vigilpay.duckdb")

def run_dlt_pipeline(csv_path=SAMPLE_CSV_PATH):
    print("\n[+] Starting Data Ingestion Pipeline...")
    if not os.path.exists(csv_path):
        print(f"[!] Sample CSV not found. Generating sample first...")
        sys.path.append(DATA_DIR)
        from generate_sample import create_stratified_sample
        csv_path = create_stratified_sample()

    df = pd.read_csv(csv_path)
    df['load_timestamp'] = datetime.utcnow().isoformat()

    if HAS_DLT:
        print("[+] Running dlt pipeline with DuckDB destination...")
        pipeline = dlt.pipeline(
            pipeline_name="paysim_ingestion",
            destination="duckdb",
            dataset_name="vigilpay_raw"
        )
        load_info = pipeline.run(
            df.to_dict(orient="records"),
            table_name="raw_transactions",
            write_disposition="append"
        )
        print(f"[OK] dlt Pipeline completed: {load_info}")
    else:
        print("[+] dlt package loading raw data directly into DuckDB...")
        conn = duckdb.connect(DB_PATH)
        conn.execute("CREATE SCHEMA IF NOT EXISTS vigilpay_raw;")
        
        # Check if table exists
        tables = conn.execute("SHOW TABLES;").fetchall()
        table_names = [t[0] for t in tables]
        
        if "raw_transactions" not in table_names:
            conn.execute("CREATE TABLE vigilpay_raw.raw_transactions AS SELECT * FROM df;")
        else:
            conn.execute("INSERT INTO vigilpay_raw.raw_transactions SELECT * FROM df;")
            
        row_count = conn.execute("SELECT COUNT(*) FROM vigilpay_raw.raw_transactions;").fetchone()[0]
        conn.close()
        print(f"[OK] Ingestion completed directly to DuckDB (vigilpay_raw.raw_transactions). Total rows: {row_count:,}")

if __name__ == "__main__":
    run_dlt_pipeline()
