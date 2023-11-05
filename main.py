from src.changer import InfoChanger, ChangeMode
from src.scraper import AuthorScraper
import orjson


def change_names(email, password):
    # There are two modes: direct_change and changes_in_json
    # Look at docstring of InfoChanger for more
    changer = InfoChanger(email, password, ChangeMode.changes_in_json)
    changer.change_info('data/authors.json', max_tabs=10)


def scrape_names(email, password, symbols):
    scraper = AuthorScraper(email, password)
    scraper.scrape_authors_info_into_file(symbols)


if __name__ == "__main__":
    email = 's22@test.test'
    password = 'FV79GBUC'
    change_names(email, password)

