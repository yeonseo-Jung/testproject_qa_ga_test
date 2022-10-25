import time
import socket
import pickle
import time
from tqdm import tqdm
from datetime import datetime

# Crawling
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from user_agent import generate_user_agent
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

import requests
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException

from request_test import run_step, get_url

def open_window():
    # # get box office movies
    # week = input('\n\nEnter the box office week: ')
    # titles = get_boxoffice_rank(week)

    # get url & open webdriver
    # url = 'https://app.testproject.io/#/projects/368433/test/4491883/recorder/mobile'    # request
    url = 'https://app.testproject.io/#/projects/368433/test/4511240/recorder/mobile'    # keytalk
    wd = get_url(url, window=True, image=True)
    time.sleep(5)

    ## Login
    email = 'yeonseosla@mycelebs.com'
    pw = 'Jys1013011!'

    elm_email = wd.find_element(By.ID, 'username')
    elm_pw = wd.find_element(By.ID, 'password')

    # input login info
    elm_email.send_keys(email)
    elm_pw.send_keys(pw)

    # click login button
    wd.find_element(By.ID, 'tp-sign-in').click()

    time.sleep(60)

    # view device
    xpath = '/html/body/div[1]/div[1]/div/div[1]/div/div[1]/div/main/div[3]/div[2]/v2-route-recorder-mobile/tp-recorder-widget/tp-movable/tp-resizable/div[1]/div/div[1]/div[1]/div[3]/div[2]'
    wd.find_element(By.XPATH, xpath).click()

    print('\n\nPlease wait one minute...')
    time.sleep(60)
    
    return wd

def reset_app(wd):
    status, cnt = 0, 0
    while status != 1 and cnt < 5:
        # reset app
        step_num = 1
        wd, status = run_step(step_num, wd)
        cnt += 1
        
    time.sleep(15)
    
    return wd, status

def select_keytalks(wd):
    # Select key talk rank 1: 10 
    
    cnt = 0
    while cnt < 10: # 키토크 섹션 한개당 10번 반복
        for i in range(8, 20):
            # 키토크 1: 10위 클릭
            wd, status = run_step(i, wd)
            time.sleep(1.5)
            
        for i in range(20, 22):
            # back & reset keytalk
            wd, status = run_step(i, wd)
            time.sleep(2)
        
        ck = True
        while status != 1:
            # reset app
            wd, status = reset_app(wd)
            
            # go to current keytalk section
            for i in range(2, 7):
                wd, status = run_step(i, wd)
                time.sleep(2)
            for i in range(keytalk_cnt):
                wd, status = run_step(23, wd)
            
            # view more keytalk    
            wd, status = run_step(7, wd)                    
            ck = False
            
        if ck:
            cnt += 1
            print(f"\n\nIterations: {cnt}\n")
        else:
            pass
    
    return wd, status, ck

if __name__ == '__main__':
    # get url & open window
    wd = open_window()
    
    keytalk_cnt = 0
    while keytalk_cnt < 16: # 16개 키토크 섹션 
        print("============")
        print(f'KeyTalk {keytalk_cnt}\n')
        
        # first
        if keytalk_cnt == 0:
            for i in range(2, 8):
                wd, status = run_step(i, wd)
                time.sleep(2)    
        else:
            for i in range(22, 24):
                wd, status = run_step(i, wd)
                time.sleep(2)

            wd, status = run_step(7, wd)
            time.sleep(2)
            
        if status == 1:
            wd, status, ck = select_keytalks(wd)
        else:            
            ck = True
            while status != 1:
                # reset app
                wd, status = reset_app(wd)
                
                # go to current keytalk section
                for i in range(2, 7):
                    wd, status = run_step(i, wd)
                    time.sleep(2)
                for i in range(keytalk_cnt):
                    wd, status = run_step(23, wd)
                
                # view more keytalk    
                wd, status = run_step(7, wd)                    
                ck = False
            
            wd, status, ck = select_keytalks(wd)
            
        keytalk_cnt += 1
        print("\n\n")
        
    wd.quit()