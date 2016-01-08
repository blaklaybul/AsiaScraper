import scrapy
import time
from scrapy.http import TextResponse

from spider_vars import long_url
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class TechInAsiaSpider(scrapy.Spider):
    name = "techinasia"
    allowed_domains = ["techinasia.com"]
    start_urls = [long_url + str(page) for page in xrange(1,2)]

    def __init__(self):
        self.driver = webdriver.Chrome()

    def parse(self, response):
        self.driver.get(response.url)
        time.sleep(10)
        el = self.driver.find_element_by_class_name("database__link")

        if el:
            print(el.text)

        print(reponse)
