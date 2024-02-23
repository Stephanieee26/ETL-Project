import pandas as pd
import time
from datetime import datetime

class Transform():
    def __init__(self):
        pass

    def transform(self, df):
        # 把空值去掉
        df_clean = df[(~df['Cash_Buy'].str.contains('-'))&(~df['Cash_Sell'].str.contains('-'))]
        df_clean.reset_index(drop=True, inplace=True)
        df_clean['Data_Input_Date'] = datetime.today().strftime('%Y-%m-%d')
        return df