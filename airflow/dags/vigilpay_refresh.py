"""
Apache Airflow Pipeline Refresh DAG for VigilPay.
Schedules daily sequence: dlt Ingestion -> dbt run -> dbt test.
"""

import os
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'vigilpay_admin',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'vigilpay_pipeline_refresh',
    default_args=default_args,
    description='Daily ingestion, dbt modeling, and sanity test refresh pipeline for VigilPay',
    schedule_interval='0 2 * * *',  # Daily at 02:00 AM
    catchup=False,
)

# Task 1: Ingest raw transactions via dlt
run_dlt_ingestion = BashOperator(
    task_id='run_dlt_ingestion',
    bash_command='python /opt/airflow/vigilpay_project/dlt_pipeline/pipeline.py',
    dag=dag,
)

# Task 2: Transform raw tables into intermediate & marts via dbt
run_dbt_transformations = BashOperator(
    task_id='run_dbt_transformations',
    bash_command='cd /opt/airflow/vigilpay_project/dbt_project && dbt run --profiles-dir .',
    dag=dag,
)

# Task 3: Execute dbt data quality & sanity tests
run_dbt_tests = BashOperator(
    task_id='run_dbt_tests',
    bash_command='cd /opt/airflow/vigilpay_project/dbt_project && dbt test --profiles-dir .',
    dag=dag,
)

# Define strict execution order
run_dlt_ingestion >> run_dbt_transformations >> run_dbt_tests
