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
    email = 's22@test.test'
    password = 'FV79GBUC'
    # firstly!
    #scrape_names(email, password, 'З')
    change_names_in_json(email, password)
    # after checked changed authors.json that changes of names are correct!
    ## change_names_on_website(email, password, 15)



