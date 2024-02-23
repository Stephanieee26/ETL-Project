import time
import sys
import pandas as pd
import numpy as np

from google.cloud import bigquery
import os
import pandas_gbq
from google.oauth2 import service_account

class Load():
    """寫入Big Query資料庫"""
    def __init__(self):
        pass
    def load(self, df):
        project_id = 'flight-ticket-410110'
        table_id = 'flight_ticket.Cash_Exchange_Rate'

        credentials = service_account.Credentials.from_service_account_file('/opt/airflow/dags/flight-ticket-key.json')
        pandas_gbq.to_gbq(df, table_id, project_id, credentials = credentials, if_exists = 'append')

        print(f'已存入資料到{table_id}')
