import time
import sys
import pandas as pd
import numpy as np
import undetected_chromedriver as uc
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime

from sqlalchemy import create_engine, types
from google.cloud import bigquery
import os
import pandas_gbq
from google.oauth2 import service_account


class Extract:
    def __init__(self):
        pass
    def data_format(self, text_list, soup):
        
        ## 如果跳轉頁面不正常
        if 'NT' not in text_list[2]:
            if '查看價格' in text_list:
                data_dict = {'地點': [], '機票價格': []}

                for i in range(0, len(text_list), 2):
                    data_dict['地點'].append(text_list[i])
                    data_dict['機票價格'].append(text_list[i + 1])
                
                df = pd.DataFrame(data_dict)

            else:
                no_price = []
                for i in range(len(text_list)-1):
                    if 'NT$' not in text_list[i] and 'NT$' not in text_list[i+1]:
                        no_price.append(i)

                no_price[0]

                text_list = text_list[:no_price[0]]

                data_dict = {'地點': [], '機票價格': []}

                for i in range(0, len(text_list), 2):
                    data_dict['地點'].append(text_list[i])
                    data_dict['機票價格'].append(text_list[i + 1])
                
                df = pd.DataFrame(data_dict)

            ## 加入直飛資訊
            flight_stay = soup.find_all('span', {'class':'BpkText_bpk-text__ZmFmY BpkText_bpk-text--body-default__NWNlO PriceDescription_description__ZDRkY'})
            flight_stay_text = flight_stay[:len(df)]

            text_list2 = []
            for i in flight_stay_text:
                text = i.getText()
                text_list2.append(text)

            data_dict2 = {'轉機/直飛': []}

            # 迭代列表，每次取三個元素，並加入字典
            for i in range(len(text_list2)):
                data_dict2['轉機/直飛'].append(text_list2[i])

            # 創建第二個DataFrame
            df2 = pd.DataFrame(data_dict2)

            # 把兩個dataframe組合
            df['轉機/直飛'] = df2['轉機/直飛']
            df = df[['地點', '轉機/直飛',  '機票價格']]

            df['ticket_price'] = df['機票價格'].str.strip('NT$').str.replace(',', '')

            # 把價格沒有顯示的先去除
            df = df[df['ticket_price']!='查看價格']
            df['ticket_price'] = df['ticket_price'].apply(int)

            # 從便宜的開始往下排序
            df = df.sort_values(by=['ticket_price'])[['地點', '轉機/直飛', 'ticket_price']]

            return df

        ## 如果跳轉頁面正常
        else:
            data_dict = {'地點': [], '機票價格': [], '住宿價格': []}

            # 迭代列表，每次取三個元素，並加入字典
            for i in range(0, len(text_list), 3):
                data_dict['地點'].append(text_list[i])
                data_dict['機票價格'].append(text_list[i + 1])
                data_dict['住宿價格'].append(text_list[i + 2])

            # 創建DataFrame
            df = pd.DataFrame(data_dict)

            ## 加入直飛資訊和住宿文字欄位
            flight_stay_text = soup.find_all('span', {'class':'BpkText_bpk-text__ZmFmY BpkText_bpk-text--body-default__NWNlO PriceDescription_description__ZDRkY'})

            text_list2 = []
            for i in flight_stay_text:
                text = i.getText()
                text_list2.append(text)
            
            data_dict2 = {'轉機/直飛': [], '飯店資訊': []}

            # 迭代列表，每次取三個元素，並加入字典
            for i in range(0, len(text_list2), 2):
                data_dict2['轉機/直飛'].append(text_list2[i])
                data_dict2['飯店資訊'].append(text_list2[i + 1])

            # 創建第二個DataFrame
            df2 = pd.DataFrame(data_dict2)

            # 把兩個dataframe組合
            df['轉機/直飛'] = df2['轉機/直飛']
            df['飯店資訊'] = df2['飯店資訊']
            df = df[['地點', '轉機/直飛',  '機票價格', '飯店資訊', '住宿價格']]

            df['ticket_price'] = df['機票價格'].str.strip('NT$').str.replace(',', '')

            # 把價格沒有顯示的先去除
            df = df[df['ticket_price']!='查看價格']
            df['ticket_price'] = df['ticket_price'].apply(int)

            # 從便宜的開始往下排序
            df = df.sort_values(by=['ticket_price'])[['地點', '轉機/直飛', 'ticket_price']]

            return df


    def crawler(
            self,
            destination_country: str,
            startdate_yymmdd: str,
            enddate_yymmdd: str
    ) -> pd.DataFrame:
        """
        skyscanner網址
        https://www.skyscanner.com.tw
        """

        options = webdriver.ChromeOptions()
        #driver = webdriver.Remote("http://127.0.0.1:4444/wd/hub", DesiredCapabilities.CHROME)
        driver = webdriver.Remote("http://172.19.0.3:4444/wd/hub", options=options)
        #driver = webdriver.Chrome()

        url = f'https://www.skyscanner.com.tw/transport/flights/tpet/{destination_country}/{startdate_yymmdd}/{enddate_yymmdd}/?adultsv2=2&cabinclass=economy&childrenv2=&ref=home&rtn=1&preferdirects=true&outboundaltsenabled=false&inboundaltsenabled=false'

        ## 把視窗最大化
        driver.maximize_window()

        driver.get(url)

        time.sleep(5)

        # 把視窗滑到底
        lastHeight = driver.execute_script("return document.documentElement.scrollHeight")
        print('lastHeight', lastHeight)

        while True:

            time.sleep(10)

            driver.execute_script("var scrollingElement = (document.scrollingElement || document.body);scrollingElement.scrollTop = scrollingElement.scrollHeight;")
            height = driver.execute_script("return document.documentElement.scrollHeight")
            newHeight = driver.execute_script("window.scrollTo(0, " + str(height) + ");")
            time.sleep(15)
            if newHeight == lastHeight:
                break
            lastHeight = newHeight
        
        # 解析網頁內容
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")

        driver.quit()

        ## 獲取機票跟住宿的價格資訊 
        destination_price = soup.find_all('span', {'class':'BpkText_bpk-text__ZmFmY BpkText_bpk-text--heading-4__MTNhO'})

        text_list = []
        for i in destination_price:
            text = i.getText()
            text_list.append(text)

        # 檢查一下資料長怎樣
        # pd.DataFrame(text_list).to_csv(f'{destination_country}_{startdate_yymmdd}.csv')
        
        df = self.data_format(text_list, soup)
        
        # 加入國家、start_date、end_date和資料更新的日期
        df['Destination_Country'] = destination_country
        df['Start_Date'] = startdate_yymmdd
        df['End_Date'] = enddate_yymmdd
        df['Data_Input_Date'] = datetime.today().strftime('%Y-%m-%d')
        
        return df    
