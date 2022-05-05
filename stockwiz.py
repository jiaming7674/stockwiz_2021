import numpy as np
from os import listdir
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import json
import time


class StockWiz():

    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--window-size=1200,1024')
        #options.add_argument('user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"')
        #options.add_experimental_option('excludeSwitches', ['enable-logging'])
        #options.add_argument('--disable-gpu')
        options.add_argument("--disable-blink-features=AutomationControlled")
        #options.add_argument('--no-sandbox')
        #options.add_argument("--disable-javascript") 
        #options.add_argument('--hide-scrollbars')
        #options.add_argument('blink-settings=imagesEnabled=false')
        #options.add_argument('--headless')
        #options.add_experimental_option("excludeSwitches", ["enable-automation"])
        #options.add_experimental_option('useAutomationExtension', False)
        #options.add_experimental_option("prefs", {"profile.password_manager_enabled": False, "credentials_enable_service": False})        
        self.driver = webdriver.Chrome(executable_path='./chromedriver.exe', chrome_options=options)
        #self.driver = webdriver.Edge(executable_path='./msedgedriver.exe')


    # def __del__(self):
    #     self.driver.quit()


    def download_stock_basic_info_from_goodinfo(self, stock_id):

        url='https://goodinfo.tw/StockInfo/StockDetail.asp?STOCK_ID=' + str(stock_id)

        self.driver.get(url)

        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, 'FINANCE_INCOME'))
            )
            print('GET : ' + str(url) + ' [OK]')
        except:
            raise Exception(url + ' [Error]')

        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        # Get the table at the top of the main page.
        soup_table_main = soup.find('table', class_='b1 p4_2 r10')

        soup_stock_name = soup_table_main.find('table', class_='b0').find('a', class_='link_blue')

        stock_id = soup_stock_name.text[0:4]
        stock_name = str.strip(soup_stock_name.text[4:])

        # Get 3rd row, include open, close, high, low
        soup_trs = soup_table_main.find_all('tr')
        soup_tds = soup_trs[3].find_all('td')

        close = float(str.strip(soup_tds[0].text))
        open = float(str.strip(soup_tds[5].text))
        high = float(str.strip(soup_tds[6].text))
        low = float(str.strip(soup_tds[7].text))
        change = float(str.strip(soup_tds[2].text))

        # Get 5th, include volumn, PBR, PER
        soup_tds = soup_trs[5].find_all('td')
        volumn = int(str.strip((soup_tds[0].text).replace(',', '')))
        try:
            PBR = float(str.strip(soup_tds[5].text))
        except:
            PBR = 0

        try:
            PER = float(str.strip(soup_tds[6].text))
        except:
            PER = 0
            
        try:
            PEG = float(str.strip(soup_tds[7].text))
        except:
            PEG = 0

        # Get stock information 
        soup_table_info = soup.find('table', class_='b1 p4_4 r10')
        soup_trs = soup_table_info.find_all('tr')
        group = soup_trs[2].find_all('td')[1].text
        market = soup_trs[3].find_all('td')[1].text
        capital = float(soup_trs[4].find_all('td')[1].text.replace(',', '').replace('億', ''))

        # Get monthly income data
        soup_table_monthly_income = soup.find('table', class_='b1 p4_2 r0_10 row_bg_2n row_mouse_over')
        soup_trs = soup_table_monthly_income.find_all('tr')
        soup_tds = soup_trs[2].find_all('td')

        MoM = float(str.strip(soup_tds[2].text))
        YoY = float(str.strip(soup_tds[3].text))
        Yacc = float(str.strip(soup_tds[5].text))

        # Get cash dividend
        soup_table_cash_dividend = soup.find('table', id='FINANCE_DIVIDEND')
        soup_trs = soup_table_cash_dividend.find_all('tr')
        cash_dividend = soup_trs[5].find_all('td')[3].text

        data = {
            'stock_id' : stock_id,
            'name' : stock_name,
            'market' : market,
            'group' : group,
            'close': close,
            'open' : open,
            'high' : high,
            'low' : low,
            'change' : change,
            'volumn' : volumn,
            'market_value' : capital * close / 10,
            'capital' : capital,
            'PBR' : PBR,
            'PER' : PER,
            'PEG' : PEG,
            'MoM' : MoM,
            'YoY' : YoY,
            'Yacc' : Yacc,
            'cash_dividend' : cash_dividend,
        }

        return data
        


    def download_stock_profit_eps_roe_from_goodinfo(self, stock_id):

        # example : https://goodinfo.tw/StockInfo/StockBzPerformance.asp?STOCK_ID=2377&YEAR_PERIOD=9999&RPT_CAT=M_QUAR
        url = 'https://goodinfo.tw/StockInfo/StockBzPerformance.asp?STOCK_ID=' + str(stock_id) + '&YEAR_PERIOD=9999&RPT_CAT=M_QUAR'

        self.driver.get(url)

        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, 'txtFinDetailData'))
            )
            print('GET : ' + str(url) + ' [OK]')
        except:
            raise Exception(url + ' [Error]')

        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        soup_table_main = soup.find('table', id='tblDetail')
        soup_trs = soup_table_main.find_all('tr', attrs={'align':'center'})

        cnt = 0
        gross_profit_margin = []
        net_operating_profit_margin = []
        pre_tax_operating_profit_margin = []
        nopat_margin = []

        roe = []
        roa = []
        eps = []

        roe4 = 0
        roa4 = 0
        eps4 = 0

        for tr in soup_trs:
            tds = tr.find_all('td')
            if (str.strip(tds[1].text) != '-'): # 股本
                try:
                    gross_profit_margin.append(float(str.strip(tds[12].text)))
                    net_operating_profit_margin.append(float(str.strip(tds[13].text)))
                    pre_tax_operating_profit_margin.append(float(str.strip(tds[14].text)))
                except:
                    gross_profit_margin.append(0)
                    net_operating_profit_margin.append(0)
                    pre_tax_operating_profit_margin.append(0)

                nopat_margin.append(float(str.strip(tds[15].text)))

                roe.append(float(str.strip(tds[16].text)))
                roa.append(float(str.strip(tds[18].text)))
                eps.append(float(str.strip(tds[20].text)))

                cnt += 1
                if cnt == 5:
                    break

        for i in range(4):
            roe4 += roe[i]
            roa4 += roa[i]
            eps4 += eps[i]

        if eps[1] <= 0:
            seasonIncrement = 0
        else:
            seasonIncrement = round((eps[0]/eps[1] - 1) * 100, 2)

        if eps[4] <= 0:
            yearIncrement = 0
        else:
            yearIncrement = round((eps[0]/eps[4] - 1) * 100, 2)

        data = {
            'gross_profit_margin' : gross_profit_margin[0],
            'net_operating_profit_margin' : net_operating_profit_margin[0],
            'pre_tax_operating_profit_margin' : pre_tax_operating_profit_margin[0], #稅前淨利率
            'nopat_margin' : nopat_margin[0], # 稅後淨利率,
            'ROE' : roe[0],
            'ROE4' : round(roe4 , 2),
            'ROA' : roa[0],
            'ROA4' : round(roa4, 2),
            'EPS' : eps[0],
            'EPS4' : eps4,
            'seasonIncrement' : seasonIncrement,
            'yearIncrement' : yearIncrement,
        }

        return data


    def download_stock_data_from_goodinfo(self, stock_id):

        downloaded_data = []

        downloaded_data.append(self.download_stock_basic_info_from_goodinfo(stock_id))
        time.sleep(5)
        downloaded_data.append(self.download_stock_profit_eps_roe_from_goodinfo(stock_id))
        time.sleep(5)

        data = {}
        for d in downloaded_data:
            for key in d.keys():
                data[key] = d[key]

        return data


    def download_stock_data_and_save_json(self,stock_list):

        return_list = []
        err_list = []

        for stock_id in stock_list:
            retry = 2
            while retry != 0:
                try:
                    data = self.download_stock_data_from_goodinfo(stock_id)

                    file_path = './data/' + str(stock_id)

                    fp = open(file_path, 'w', encoding='utf8')
                    json.dump(data, fp, ensure_ascii=False)
                    fp.close()

                    return_list.append(stock_id)
                    break
                except Exception as e:
                    print("Error : " + str(stock_id))
                    print(">>>" + str(e))
                    retry -= 1
                    if retry == 0:
                        err_list.append(stock_id)
                        print("Download Fail ... " + str(stock_id) + "  [Fail]")
                
                time.sleep(5)

        return return_list, err_list


    def read_json_file_to_csv(self):

        ls_dir = listdir('./data')
        downloaded_data = []

        for file_name in ls_dir:
            downloaded_data.append(file_name)

        dic = {}
        
        for stock_id in downloaded_data:
            fp = open('./data/' + str(stock_id), 'r', encoding='utf8')
            d = json.load(fp)
            dic[str(stock_id)] = d
            fp.close()

        df = pd.DataFrame(dic)
        df = df.transpose()

        df.to_csv('stockwiz.csv', encoding='utf-8')


    def read_list_and_find_not_existed(self):

        list_arr = []
        fp = open('./list', 'r')
        lines = fp.readlines()
        fp.close()
        for line in lines:
            n = int(str.strip(line))
            try:
                list_arr.index(n)
                print('duplicate : ' + str(n))
            except:
                list_arr.append(n)

        ls_dir = listdir('./data')

        downloaded_data = []

        for file_name in ls_dir:
            d = int(str.strip(file_name))
            downloaded_data.append(d)

        need_to_be_download = []

        for stock_id in list_arr:
            try:
                downloaded_data.index(stock_id)
            except:
                need_to_be_download.append(stock_id)

        return need_to_be_download 


def read_list():
    list_arr = []
    fp = open('./list', 'r')
    lines = fp.readlines()
    for line in lines:
        n = int(str.strip(line))
        try:
            list_arr.index(n)
            print('duplicate : ' + str(n))
        except ValueError:
            list_arr.append(n)
    fp.close()

    return list_arr