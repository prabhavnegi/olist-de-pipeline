FROM apache/airflow:latest

RUN python -m venv /opt/airflow/dbt_venv \
    && /opt/airflow/dbt_venv/bin/pip install --no-cache-dir dbt-postgres

# Look at the end of the pipeline_venv block and add "psycopg[binary]"
RUN python -m venv /opt/airflow/pipeline_venv \
    && /opt/airflow/pipeline_venv/bin/pip install --no-cache-dir \
        pandas SQLAlchemy psycopg2-binary python-dotenv "psycopg[binary]"
