import re
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyquery import PyQuery as pq
import pymongo
from Config import *

browser = webdriver.Chrome()
wait = WebDriverWait(browser, 10)
client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]

def search():
    browser.get("http://www.taobao.com/")
    try:
        input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#q'))
        )
        submit = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '#J_TSearchForm > div.search-button > button'))
        )
        input.clear()
        input.send_keys('美食')
        submit.click()
        total = wait.until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="mainsrp-pager"]/div/div/div/div[1]'))
        )
        get_product()
        return total.text
    except TimeoutException:
        return search()

def next_page(page_number):
    try:
        input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > input'))
        )                                                     #mainsrp-pager > div > div > div > div.form > input
        submit = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit'))
        )
        input.clear()
        input.send_keys(page_number)
        submit.click()
        wait.until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > ul > li.item.active > span'), str(page_number))
        )
        get_product()
    except TimeoutException:
        print('a...时间太长了')

def get_product():
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-itemlist .items .item')))
        html = browser.page_source
        doc = pq(html)
        items = doc('#mainsrp-itemlist .items .item.J_MouserOnverReq').items()
        for item in items:
            product = {
                'image': item.find('.pic .img').attr('src'),
                'price': item.find('.price').text(),
                'deal': item.find('.deal-cnt').text()[:-3],
                'title': item.find('.J_ClickStat').text(),
                'shopname': item.find('.shopname').text(),
                'location': item.find('.location').text(),

            }
            save_to_mongo(product)
    except Exception:
        return None

def save_to_mongo(result):
    try:
        if db[MONGO_TABLE].insert(result):
            print('存储到MONGODB成功', result)
    except Exception:
        print('存储出错啦')

def main():
    try:
        total = int(re.search('(\d+)', search()).group(1))
        for next in range(2, total + 1):
            print('********************************************现在是第', next, '页********************************************')
            next_page(next)
    except Exception:
        print('main()')
    finally:
        browser.close()


if __name__ == '__main__':
    main()