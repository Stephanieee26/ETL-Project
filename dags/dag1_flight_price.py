from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.contrib.operators.bigquery_check_operator import BigQueryCheckOperator
import datetime as dt

import time
import pandas as pd
import numpy as np
import undetected_chromedriver as uc
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime

from google.cloud import bigquery
import os
import pandas_gbq
from google.oauth2 import service_account

import sys
sys.path.append('/opt/airflow/dags')

## airflow環境這行要刪掉
## sys.path.append('/Users/stephanie/airflow_docker/dags')

from extract import Extract
from transform import Transform
from load import Load

# 定義每個task的函數

def run_etl_JP(country, startdate, enddate):
    df = Extract().crawler(country, startdate, enddate)
    transform_df = Transform().transform(df)
    print(transform_df.head())
    Load().load(transform_df)

def run_etl_HK(country, startdate, enddate):
    df = Extract().crawler(country, startdate, enddate)
    transform_df = Transform().transform(df)
    print(transform_df.head())
    Load().load(transform_df)

def run_etl_KR(country, startdate, enddate):
    df = Extract().crawler(country, startdate, enddate)
    transform_df = Transform().transform(df)
    print(transform_df.head())
    Load().load(transform_df)

# Dag

default_args = {
    'owner': 'Stephanie',
    'retries': 5,
    'retry_delay': dt.timedelta(minutes=3),
    'email_on_retry': False,
    'email_on_failure': False,
}

dag = DAG(
    'flight_ticket',
    default_args = default_args,
    start_date = dt.datetime(2024, 1, 11, 8, 35, 0),
    schedule_interval = dt.timedelta(hours=4),
    catchup = False
)

with dag:
    task1 = PythonOperator(
        task_id = "JP",
        python_callable = run_etl_JP('JP', '240404', '240407'),
        #dag = dag
    )

    task2 = PythonOperator(
        task_id = "HK",
        python_callable = run_etl_HK('HK', '240404', '240407'),
        #dag = dag
    )

    task3 = PythonOperator(
        task_id = "KR",
        python_callable = run_etl_KR('KR', '240404', '240407'),
        #dag = dag
    )

    task1 >> task2 >> task3

