import pandas as pd
import time
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
#from airflow.contrib.operators.bigquery_check_operator import BigQueryCheckOperator

from extract2 import Extract
from transform2 import Transform
from load2 import Load

def etl():
    df = Extract().extract()
    transform_df = Transform().transform(df)
    print(transform_df.head())
    Load().load(transform_df)

# Dag
default_args = {
    'owner': 'Stephanie',
    'retries': 10,
    'retry_delay': timedelta(minutes=10),
    'email_on_retry': False,
    'email_on_failure': False,
}

dag = DAG(
    dag_id = 'exchange_rate',
    default_args = default_args,
    start_date = datetime(2024, 2, 6, 0, 0, 0),
    schedule_interval = timedelta(hours=4),
    catchup = False
)

with dag:
    task = PythonOperator(
        task_id = "Currency",
        python_callable = etl
    )

