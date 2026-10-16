from datetime import datetime

from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator

PROJECT = "/opt/airflow/project"
PIPELINE_PY = "/opt/airflow/pipeline_venv/bin/python"
DBT = "/opt/airflow/dbt_venv/bin/dbt"

with DAG(
    dag_id="olist_pipeline",
    description="Ingest Olist CSVs into raw, build the star schema with dbt, then test it",
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["olist", "elt"],
) as dag:

    ingest_raw = BashOperator(
        task_id="ingest_raw",
        bash_command=f"cd {PROJECT}/scripts && {PIPELINE_PY} -m ingest",
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=f"cd {PROJECT}/olist_dbt && {DBT} run",
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"cd {PROJECT}/olist_dbt && {DBT} test",
    )

    ingest_raw >> dbt_run >> dbt_test