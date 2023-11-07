from time import sleep
import re

from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
import orjson
from loguru import logger

from .base import WebDriverMixin, Participant


class AuthorScraper(WebDriverMixin):
    '''
    The AuthorScraper class is a subclass of the WebDriverMixin class.
    It provides methods to scrape information about authors from a
    website using Selenium and store the data in a JSON file.\n
    There are 2 methods:\n
    1) *scrape_authors_info_into_file* scraping info and saving it into json file.
    2) *get_authors_info_as_dict* scraping info and returning it without saving.
    '''
    def __init__(self, email, password):
        super().__init__(email,password)

    def _get_authors_info(self, symbols: str, start: int, end: int) -> list:
        participants = list()
        try:
            self.driver.get("https://orgm.riep.ru/cabinet/authors.php")
            filter_elem = self.driver.find_element(By.ID, 'col1_filter')
            filter_elem.send_keys(symbols)
            self.driver.find_element(By.CLASS_NAME, "btn-label").click()
            list_len = self.driver.find_element(By.NAME, 'alist_length')
            #some condition - стартовое значение start и конечное значение end (1200,2400)

            Select(list_len).select_by_value('200')
            sleep(5)
            pattern = r"^[А-ЯЁ][а-яё]+ [А-ЯЁ]\. [А-ЯЁ]\.$"
            #count_pages = 0
            #сначала прокрутка до старта - после этого начинается работа алгоритма
            #while count_pages*200 < start
            #count_pages++
            #next_page_click()

            #while count_pages*200 < end
            while True:
                table = self.driver.find_element(By.XPATH, ".//tbody")
                rows = table.find_elements(By.CSS_SELECTOR, 'tr')
                for row in rows:
                    name = row.find_element(By.XPATH, ".//a[@class='link-dark']").text.encode('utf-8').decode('utf-8')
                    if re.match(pattern, name):
                        continue
                    link = row.find_element(By.XPATH, ".//a[@class='link-primaru text-end']").get_attribute('href')
                    participants.append(Participant(name, link)._asdict())
                next_page = self.driver.find_element(By.XPATH, "//li[@id='alist_next']")
                if next_page.get_attribute('class') == 'paginate_button page-item next disabled':
                    break
                else:
                    #count pages++
                    next_page.click()
                sleep(3)
        except:
            logger.warning('Error occured while getting names from website')
        return participants

    def scrape_authors_info_into_file(self, symbols: str, filepath: str = 'data/authors.json') -> None:
        '''
        The scrape_authors_info_into_file method is a part of the AuthorScraper class. It scrapes information
        about authors from a website using Selenium and saves the data in a JSON file.\n
        **Example Usage**\n
        scraper = AuthorScraper(email, password)\n
        scraper.scrape_authors_info_into_file(symbols, filepath)\n
        **Inputs**\n
        symbols (string): The start symbols to filter the authors.\n
        filepath (string, optional): The file path to save the scraped data. Default is 'data/authors.json'.
        '''
        participants = self._get_authors_info(symbols)
        if not len(participants):
            logger.critical('No authors were scrapped! Are start symbols right?')
            return
        logger.debug(f"{len(participants)} authors were scraped, parsing them in {filepath}")
        with open(filepath, 'wb') as file:
            file.write(orjson.dumps(participants))

    def get_authors_info_as_dict(self, symbols: str) -> list:
        '''
        The get_authors_info_as_dict method is a part of the AuthorScraper class.
        It retrieves information about authors from a website using Selenium and returns the data
        as a list of dictionaries.\n
        **Example Usage**\n
        scraper = AuthorScraper(email, password)\n
        authors_info = scraper.get_authors_info_as_dict(symbols)\n
        print(authors_info)\n
        **Inputs**\n
        symbols (string): The start symbols to filter the authors.\n
        '''
        participants = self._get_authors_info(symbols)
        if not len(participants):
            logger.critical('Got no authors! Are start symbols right?')
            return []
        return participants
