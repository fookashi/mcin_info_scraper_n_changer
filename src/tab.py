from time import sleep
from collections import deque

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


class ChangeTabInfoTask:

    def __init__(self, driver, link, new_name):
        super().__init__()
        self.driver = driver
        self.link = link
        self.new_name = new_name

    def run(self):
        self.driver.execute_script("window.open('', '_blank');")
        self.driver.switch_to.window(self.driver.window_handles[-1])
        self.driver.get(self.link)
        body = self.driver.find_element(By.CSS_SELECTOR, 'body')
        fio = body.find_element(By.NAME, 'fio')
        fio.clear()
        self.driver.execute_script("arguments[0].value = arguments[1];", fio, self.new_name)
        fio.submit()

