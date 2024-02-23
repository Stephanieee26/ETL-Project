import time
import sys
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

from sqlalchemy import create_engine, types
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
        table_id = 'flight_ticket.Crawl_Flight_Ticket_New'

        credentials = service_account.Credentials.from_service_account_file('/opt/airflow/dags/flight-ticket-key.json')
        pandas_gbq.to_gbq(df, table_id, project_id, credentials = credentials, if_exists = 'append')

        print(f'已存入資料到{table_id}')
