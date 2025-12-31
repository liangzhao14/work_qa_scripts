from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from time import sleep

webdriver_path = r'D:\tools\chromedriver-win64\chromedriver.exe'
service = Service(executable_path=webdriver_path)
wd = webdriver.Chrome(service=service)
wd.implicitly_wait(3)
wd.get("")
sleep(3)


wd.quit()