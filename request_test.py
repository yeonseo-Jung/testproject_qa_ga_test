import time
import socket
import pickle
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

def get_headers():
    userAgent = generate_user_agent(os=('mac', 'linux'), navigator='chrome', device_type='desktop')
    headers = {
        "user-agent": userAgent,
        "Accept": "application/json",
    }
    return headers

def get_url(url, window=False, image=False):
    ''' Set up webdriver, useragent & Get url '''
    
    wd = None
    socket.setdefaulttimeout(30)
    error = []
    attempts = 0 # url parsing 시도횟수
    # 10번 이상 parsing 실패시 pass
    while attempts < 10:
        try:  
            attempts += 1
            # user agent
            options = Options() 
            userAgent = generate_user_agent(os=('mac', 'linux'), navigator='chrome', device_type='desktop')
            options.add_argument("--disable-gpu")
            options.add_argument('--disable-extensions')
            options.add_argument(f'user-agent={userAgent}')
            options.add_argument("--start-fullscreen")
            
            if not window:
                options.add_argument('headless')
            if not image:
                options.add_argument('--blink-settings=imagesEnabled=false')

            # web driver 
            wd = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
            wd.get(url)
            wd.implicitly_wait(5)
            break

        # 예외처리
        except Exception as e:
            print(f'\n\nError: {str(e)}\n\n')
            
            time.sleep(30)
            try:
                wd.quit()
            except:
                pass
            wd = None
    return wd

def json_iterator(url, headers=True):
    
    if headers:
        headers = get_headers()
    else:
        headers = None
    res_data = requests.get(url, headers=headers)
    
    return res_data

def check_step(wd):
    # check running step successful
    soup = BeautifulSoup(wd.page_source, 'lxml')
    if soup.find('div', 'execution-result failed') is None and soup.find('div', 'execution-result ng-star-inserted failed') is None:
        status = 1
    else:
        status = 0

    return wd, status

def reset_app(wd):
    status, cnt = 0, 0
    while status != 1 and cnt < 5:
        # reset app
        step_num = 20
        wd, status = run_step(step_num, wd)
        cnt += 1
        
    time.sleep(15)
    
    return wd, status

def go_home(wd):
    # init app (go to the home)  
    step_num = 1
    wd, status = run_step(step_num, wd)
    time.sleep(3)
    step_num = 16
    wd, status = run_step(step_num, wd)
    time.sleep(3)
    
    if status != 1:
        wd, status = reset_app(wd)
    
    return wd, status

def run_step(step_num, wd):
    
    ''' Running step
    status  
    *  1: successful
    *  0: failed
    * -1: error
    '''

    # click step 
    xpath_step = f'/html/body/div[1]/div[1]/div/div[1]/div/div[1]/div/main/div[3]/div[2]/v2-route-recorder-mobile/tp-recorder-widget/tp-movable/tp-resizable/div[1]/div/div[3]/tp-recorder-steps/div/tp-a-scroll/div/tp-recorder-step[{step_num}]/div/div/div[1]/div[2]/span'
    wd.find_element(By.XPATH, xpath_step).click()

    # run step
    xpath_run = '/html/body/div[1]/div[1]/div/div[1]/div/div[1]/div/main/div[3]/div[2]/v2-route-recorder-mobile/tp-recorder-widget/tp-movable/tp-resizable/div[1]/div/div[2]/div[2]/div/div[3]/div[1]/tp-dynamic-template/tp-svg-icon-play-arrow'
    wd.find_element(By.XPATH, xpath_run).click()
    time.sleep(2.5)

    # check running step successful
    try:
        element = WebDriverWait(wd, 5).until(
            EC.element_to_be_clickable((By.XPATH, xpath_step))
        )
        
        # check running step successful
        wd, status = check_step(wd)
            
    except TimeoutException:
        status = -1

    if status == 1 or status == 0:
        pass
    else:
        # check cancel button
        xpath_cancel = '/html/body/tp-wizard-dialog/div/div/div[2]/tp-dynamic-template/tp-recorder-execution-self-healing/div/div[3]/div[1]'
        try:
            element = WebDriverWait(wd, 30).until(
                EC.element_to_be_clickable((By.XPATH, xpath_cancel))
            )  
            time.sleep(1.5)
            wd.find_element(By.XPATH, xpath_cancel).click()
            status = 0         
        except TimeoutException:
            status = -1

        if status == -1:
            # check running step successful
            try:
                element = WebDriverWait(wd, 30).until(
                    EC.element_to_be_clickable((By.XPATH, xpath_step))
                )
                
                # check running step successful
                wd, status = check_step(wd)
                    
            except TimeoutException:
                status = -1
                
    print(f'Step {step_num}: {status}')                         
    return wd, status

def search_movie(wd, title):

    # run step 1, 2, 15, 2
    wd, status = run_step(1, wd) # click search button
    wd, status = run_step(2, wd) # click search box
    wd, status = run_step(15, wd) # click cancel button (init search words)
    wd, status = run_step(2, wd) # click search box

    ## click search box
    xpath = '/html/body/div[1]/div[1]/div/div[1]/div/div[1]/div/main/div[3]/div[2]/v2-route-recorder-mobile/tp-device-mirror/tp-movable'
    elm_simulator = wd.find_element(By.XPATH, xpath)

    # aim offset: 480 * 360 
    # move to search box
    ActionChains(wd).move_to_element_with_offset(elm_simulator, xoffset=-25, yoffset=-245).perform()
    time.sleep(2.5)

    # click search box
    ActionChains(wd).click(on_element=None).perform()
    time.sleep(2.5)

    # input text (movie title)
    xpath = '/html/body/div[1]/div[1]/div/div[1]/div/div[1]/div/main/div[3]/div[2]/v2-route-recorder-mobile/tp-d-m-record-type-text/tp-d-m-record-type-text-input/div[2]/tp-input/input'
    elm_search_box = wd.find_element(By.XPATH, xpath)
    elm_search_box.clear()
    elm_search_box.send_keys(title)
    time.sleep(2.5)

    # click Search button
    xpath = '/html/body/div[1]/div[1]/div/div[1]/div/div[1]/div/main/div[3]/div[2]/v2-route-recorder-mobile/tp-d-m-record-type-text/tp-d-m-record-type-text-input/div[3]/div[2]/tp-svg-icon-v'
    wd.find_element(By.XPATH, xpath).click()
    time.sleep(5)
    # click movie
    step_num = 3
    wd, status = run_step(step_num, wd)
    
    if status != 1:
        status = -2

    return wd, status

def run_steps(wd, title):
    ''' Running request test all steps '''

    wd, status = search_movie(wd, title)
    if status != 1:
        pass
    
    else:    
        wd, status = run_step(4, wd)
        wd, status = run_step(5, wd)

        for i in range(2):
            step_num = 18 + i
            if status == 1:
                break
            elif status == 0:
                # go to the home
                wd, status = go_home(wd)
                
                wd, status = search_movie(wd, title)
                wd, status = run_step(step_num, wd)
                wd, status = run_step(5, wd)
            else:
                # reset app
                wd, status = reset_app(wd)
                
                wd, status = search_movie(wd, title)
                wd, status = run_step(step_num, wd)
                wd, status = run_step(5, wd)

        if status == 1:   
            # click platform name & request
            for step_num in range(7, 15):
                wd, status = run_step(step_num, wd)
            
            if status == 1:
                # init app (go to the home)
                wd, status = go_home(wd)
            
    return wd, status
 
def get_boxoffice_rank(week):
    url = f'https://www.boxofficemojo.com/weekly/2022W{week}/?ref_=bo_wly_table_1'

    res_data = json_iterator(url)       
    html = BeautifulSoup(res_data.text, 'lxml')
    table = html.find('div', {'id': 'table'}).find_all('tr') 

    titles = []
    for mv in table:
        title = mv.find('td', 'a-text-left mojo-field-type-release mojo-cell-wide')
        if title is None:
            pass
        else:
            title = title.text.strip()
            if title not in titles:
                titles.append(title)
    
    return titles



if __name__=='__main__':
    # get box office movies
    week = input('\n\nEnter the box office week: ')
    titles = get_boxoffice_rank(week)
    
    # get url & open webdriver
    url = 'https://app.testproject.io/#/projects/368433/test/4491883/recorder/mobile'
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

    time.sleep(10)

    # view device
    xpath = '/html/body/div[1]/div[1]/div/div[1]/div/div[1]/div/main/div[3]/div[2]/v2-route-recorder-mobile/tp-recorder-widget/tp-movable/tp-resizable/div[1]/div/div[1]/div[1]/div[3]/div[2]'
    wd.find_element(By.XPATH, xpath).click()

    print('\n\nPlease wait one minute...')
    time.sleep(60)

    movie_dict = {}
    error = []
    for title in tqdm(titles):
        print('=======================')
        print(title)
        wd, status = run_steps(wd, title)
        if status == 1:
            movie_dict[title] = status
        elif status == -2:
            movie_dict[title] = status
            wd, status = reset_app(wd)
        else:
            cnt = 0
            while status != 1 and cnt < 2:
                # reset app
                wd, status = reset_app(wd)
                wd, status = run_steps(wd, title)
                movie_dict[title] = status
                cnt += 1

            if status != 1:
                wd, status = reset_app(wd)
                
        print('=======================')
        print('\n\n')
    
    wd.quit()    

    # save status file
    _date = datetime.today().strftime('%y%m%d')    
    file = f'request_test_status_movie_{_date}.txt'
    with open(file, 'wb') as f:
        pickle.dump(movie_dict, f)