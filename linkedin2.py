import os
import pymysql
from dotenv import load_dotenv
load_dotenv()

from selenium import webdriver
import time
from selenium.webdriver.common.keys import Keys
from urllib.request import urlopen
from bs4 import BeautifulSoup
import requests
import random

options = webdriver.ChromeOptions()
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; WOW64; rv:53.0) Gecko/20100101 Firefox/47.0')
options.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})
driver = webdriver.Chrome(executable_path = '/Users/beckyliu/individual_project/chromedriver',options=options) 

# no scroll one page
def search(position,country):
    driver.get("https://www.linkedin.com/jobs/")
    time.sleep(random.randint(1,3))
    from selenium.webdriver.common.keys import Keys
    html = driver.find_element_by_tag_name('html')
    html.send_keys(Keys.PAGE_DOWN)


    # find the keywords/location search bars:
    search_bars = driver.find_elements_by_class_name('dismissable-input__input')
    search_keywords = search_bars[2]
    search_keywords.send_keys(position)    
    search_location = search_bars[3] 
    time.sleep(5)
    search_location.send_keys(country)
    search_location.send_keys(Keys.RETURN)
    print('searched successfully!')

def getJD():
    #find jobs
    data = []
    time.sleep(5)
    jobs = driver.find_elements_by_class_name('result-card')
    print('================ New Page ================  ')
    print('how many jobs on this page: ',len(jobs)) 
    if len(jobs) == 0:
        print(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()))
        pass
        # time.sleep(random.randint(3,5))
        # search('Software Engineer','United States')
        # raise IOError("Try Again!")
    else:
        jobs = driver.find_elements_by_class_name('result-card')
        for job in jobs:
            driver.execute_script("arguments[0].scrollIntoView();", job)
            job.click()
            time.sleep(random.randint(3,5))
            # get info:
            try:
                [position, company, location, hiringStatus, postTime] = job.text.split('\n')[:5]
                print([position, company, location, hiringStatus, postTime])
                time.sleep(random.randint(1,3))
                showMore = driver.find_elements_by_class_name('show-more-less-html__button')
                showMore[0].click()
                details = driver.find_element_by_class_name("description__text").text
                # print(details)
                t = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
                data.append([position, company, location,hiringStatus,postTime,t,details])
                # data.append([position, company, location,hiringStatus,postTime])
                print('-------------- Done this Job --------------')
            except:
                continue
    return data

def saveJobs():
    all = list()
    # search('Software Engineer','United States')
    all.extend(getJD())
    print('--------------  exceute getJD() -------------- ')
    return all

def scroll():
    saveall = list()
    search('Data Engineer','United States')
    try:
        seeMoreJobs = driver.find_elements_by_class_name('infinite-scroller__show-more-button--visible')
        # while len(seeMoreJobs) < 1:
        #     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        #     time.sleep(random.randint(5,10))
        #     print(len(seeMoreJobs))
        print(seeMoreJobs[0])
        seeMoreJobs[0].click()
        print('clicked!')   
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        print('clicked and scroll') 
    except:
        # pass
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    saveall.extend(saveJobs())
    print('saveall[0]: ',saveall[0])
    return saveall

# print(saveJobs()[0:5])
# print(scroll())
# print('len(scroll()): ',len(scroll()))

def saveDB(data):
    Host = os.getenv("Host")
    User = os.getenv("User")
    Password = os.getenv("Password")
    Path = os.getenv("Path")
    connection = pymysql.connect(host=Host,
                                user=User,
                                password=Password,
                                database='JHT',
                                charset='utf8mb4',
                                cursorclass=pymysql.cursors.DictCursor)
    with connection:
        cursor = connection.cursor()
        back = cursor.executemany("INSERT INTO Job (position,company,location,status,posttime,savetodbtime,details) VALUES(%s,%s,%s,%s,%s,%s,%s)", data) 
        connection.commit()
        print('Items save to db: ',back)

saveDB(scroll())
print('Done!')
