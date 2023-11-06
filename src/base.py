from collections import namedtuple
from time import sleep
from enum import Enum

from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
from loguru import logger

Participant = namedtuple('Participant', ['name', 'link'])


class ChangeMode(Enum):
    direct_change = 0
    changes_in_json = 1
    changes_in_log = 2


class WebDriverMixin:
    '''
    The WebDriverMixin class is a mixin that provides a convenient way to initialize and
    interact with a web browser using the Selenium library. It sets up the browser with necessary extensions and options,
    logs in to a specific website, and waits for captcha solving before proceeding.
    Example Usage
    # The browser is initialized with necessary extensions and options
    # It navigates to the login page of a website and enters the provided email and password
    # It waits for captcha solving before proceeding
    Code Analysis
    Main functionalities
    Initializes a web browser with necessary extensions and options
    Logs in to a specific website using provided email and password
    Waits for captcha solving before proceeding
    '''
    def __init__(self, email: str, password: str):
        logger.debug('Started initializing web driver!')
        logger.info('Add extensions, arguments etc')
        self._update_crx()
        options = webdriver.ChromeOptions()
        options.add_extension('src/solver.crx')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')
        options.headless = False

        logger.info('Initializing browser driver')
        self.driver = webdriver.Chrome(options=options)
        self.driver.implicitly_wait(10)
        self.driver.get("https://orgm.riep.ru/cabinet/authors.php")
        email_elem = self.driver.find_element(By.ID, 'email')
        email_elem.send_keys(email)
        password_elem = self.driver.find_element(By.ID, 'password')
        password_elem.send_keys(password)
        submit_button = self.driver.find_element(By.XPATH, "//*[text()='Войти']")
        logger.info('Waiting for captcha solving.')
        curr_url = self.driver.current_url
        while self.driver.current_url == curr_url:
            sleep(3)
        logger.debug(f'Browser initialized, now {self.__class__.__name__} will do its job.')
    def _update_crx(self):
        logger.info('downloading crx file for captcha ext')
        crx_page_url = "https://chrome.google.com/webstore/detail/buster-captcha-solver-for/mpbjkejclgfgadiemmefgebjfooflfhl"
        ext_id = crx_page_url.split('/')[-1]
        download_link = f"https://clients2.google.com/service/update2/crx?response=redirect&os=crx&arch=x86-64&nacl_arch=x86-64&prod=chromecrx&prodchannel=unknown&prodversion=88.0.4324.150&acceptformat=crx2,crx3&x=id%3D{ext_id}%26uc"
        with open('src/solver.crx', 'wb') as file:
            addon_binary = requests.get(download_link).content
            file.write(addon_binary)