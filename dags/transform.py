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

class Transform:
    def __init__(self):
        pass
    def transform(self, df):
        # 更改欄位名稱
        df = df.rename(columns = {'地點':'Destination_City', '轉機/直飛':'Direct_Flight', 'ticket_price':'Ticket_Price'})
        df = df[['Destination_Country', 'Destination_City', 'Start_Date', 'End_Date', 'Direct_Flight', 'Ticket_Price', 'Data_Input_Date']]
        return df
    
