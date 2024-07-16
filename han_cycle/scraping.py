import csv
import logging
import os
import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# 돋보기 클릭
def click_icon(driver):
    driver.get("https://travel.naver.com/domestic")
    time.sleep(1)
    try:
        element = driver.find_element(By.CSS_SELECTOR, "a.header_search__4UCHI")

        # JavaScript를 실행해 ::after 가상 요소를 클릭
        driver.execute_script("arguments[0].click();", element)

    except Exception as e:
        print("버튼 못찾아따")
        print(e)
    

# 버튼 클릭 함수
def click_button_by_class(driver):
    parent_element = driver.find_element(By.CLASS_NAME, "searchbox_home_tabs__FA2_B")
    elements = parent_element.find_elements(By.CLASS_NAME, "searchbox_home_tab__RNL7F")
    for element in elements:
        element.click()
        time.sleep(1)
        button = driver.find_elements(By.CLASS_NAME, "searchbox_home_button__hVBDW")
        button.click()
        time.sleep(1)  # 클릭 후 대기 시간

def main():

    options = Options()
    #options.add_argument("--headless")
    #options.add_argument("--disable-gpu")
    #options.add_argument("--no-sandbox")
    #options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--start-maximized")


    print(ChromeDriverManager(driver_version="120").install())
    browser = webdriver.Chrome(options=options)

    click_icon(browser)
    click_button_by_class(browser)


    browser.quit()


if __name__ == "__main__":

    main()
