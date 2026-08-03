"""
Local Airflow DAG Execution Runner & Log Verifier for VigilPay.
Executes the `vigilpay_pipeline_refresh` DAG sequence:
  Task 1: run_dlt_ingestion (dlt_pipeline/pipeline.py)
  Task 2: run_dbt_transformations (dbt run)
  Task 3: run_dbt_tests (dbt test)
Reports individual task green/red status, detailed task logs, and total execution time.
"""

import os
import sys
import time
import subprocess
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DBT_DIR = os.path.join(BASE_DIR, "dbt_project")

def run_task(task_id: str, command: str, cwd: str) -> tuple:
    print(f"\n" + "="*75)
    print(f"[START TASK] {task_id}")
    print(f"  - Command : {command}")
    print(f"  - Cwd     : {cwd}")
    print("="*75)
    
    start_time = time.time()
    try:
        process = subprocess.Popen(
            command,
            cwd=cwd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        output = []
        for line in iter(process.stdout.readline, ''):
            print(f"[{task_id}] {line}", end='')
            output.append(line)
            
        process.stdout.close()
        return_code = process.wait()
        duration = round(time.time() - start_time, 2)
        
        if return_code == 0:
            print(f"\n[OK SUCCESS] Task '{task_id}' completed in {duration}s")
            return True, duration, "".join(output)
        else:
            print(f"\n[FAILED] Task '{task_id}' failed with exit code {return_code} after {duration}s")
            return False, duration, "".join(output)
    except Exception as e:
        duration = round(time.time() - start_time, 2)
        print(f"\n[EXCEPTION] Task '{task_id}' threw exception: {e}")
        return False, duration, str(e)

def run_airflow_dag_refresh():
    print(f"\n=========================================================================")
    print(f"      VIGILPAY — AIRFLOW DAG ACTUAL RUN VERIFICATION REPORT              ")
    print(f"      DAG ID: vigilpay_pipeline_refresh                                 ")
    print(f"      Execution Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}   ")
    print(f"=========================================================================")

    pipeline_start = time.time()
    tasks_summary = []

    # Task 1: run_dlt_ingestion
    t1_success, t1_dur, t1_log = run_task(
        task_id="run_dlt_ingestion",
        command=f"{sys.executable} dlt_pipeline/pipeline.py",
        cwd=BASE_DIR
    )
    tasks_summary.append({"task_id": "run_dlt_ingestion", "success": t1_success, "duration": t1_dur})

    if not t1_success:
        print("\n[!] DAG halted early due to Task 1 failure.")
        return False

    # Task 2: run_dbt_transformations
    t2_success, t2_dur, t2_log = run_task(
        task_id="run_dbt_transformations",
        command="dbt run --profiles-dir .",
        cwd=DBT_DIR
    )
    tasks_summary.append({"task_id": "run_dbt_transformations", "success": t2_success, "duration": t2_dur})

    if not t2_success:
        print("\n[!] DAG halted early due to Task 2 failure.")
        return False

    # Task 3: run_dbt_tests
    t3_success, t3_dur, t3_log = run_task(
        task_id="run_dbt_tests",
        command="dbt test --profiles-dir .",
        cwd=DBT_DIR
    )
    tasks_summary.append({"task_id": "run_dbt_tests", "success": t3_success, "duration": t3_dur})

    total_duration = round(time.time() - pipeline_start, 2)

    print("\n" + "="*75)
    print("                AIRFLOW DAG FINAL EXECUTION SUMMARY                      ")
    print("="*75)
    print(f"DAG Status       : {'ALL GREEN (SUCCESS)' if all(t['success'] for t in tasks_summary) else 'FAILED'}")
    print(f"Total Execution  : {total_duration} seconds\n")
    
    print("Task Status Breakdown:")
    for t in tasks_summary:
        status_str = "[PASS] GREEN" if t['success'] else "[FAIL] RED"
        print(f"  - {t['task_id'].ljust(26)} : {status_str} in {t['duration']}s")
    print("="*75 + "\n")

    return all(t['success'] for t in tasks_summary)

if __name__ == "__main__":
    run_airflow_dag_refresh()
