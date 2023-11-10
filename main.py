from dotenv import load_dotenv
import os

from src.changer import InfoChanger, ChangeMode
from src.scraper import AuthorScraper

import orjson


def change_names_in_json(email: str, password: str):
    # There are two modes: direct_change and changes_in_json
    # Look at docstring of InfoChanger for more
    changer = InfoChanger(email, password, ChangeMode.changes_in_json)
    changer.change_info('data/authors.json')


def change_names_on_website(email: str, password: str, max_tabs: int = 10):
    # There are two modes: direct_change and changes_in_json
    # Look at docstring of InfoChanger for more
    changer = InfoChanger(email, password, ChangeMode.direct_change)
    changer.change_info('data/authors.json', max_tabs=max_tabs)


def scrape_names(email: str, password: str, symbols: str):
    scraper = AuthorScraper(email, password)
    scraper.scrape_authors_info_into_file(symbols)


if __name__ == "__main__":
    load_dotenv()
    # type your email and password in .env file
    EMAIL = os.getenv('EMAIL')
    PASSWORD = os.getenv('PASSWORD')
    # #--------------------------------------------------------------------------#
    # # Uncomment after you've read docstrings and understood what happens there #
    # #--------------------------------------------------------------------------#
    # scrape_names(EMAIL, PASSWORD, 'З')
    # change_names_in_json(EMAIL, PASSWORD)
    # # # After you've checked 'result/changed info.json' that changes of names are correct!
    # change_names_on_website(EMAIL, PASSWORD, 15)




