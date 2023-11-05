from time import sleep

from concurrent.futures import ThreadPoolExecutor

import orjson
from selenium.webdriver.common.by import By

from src.base import WebDriverMixin, ChangeMode
from src.tab import ChangeTabInfoTask


class InfoChanger(WebDriverMixin):
    '''
    The InfoChanger class is a subclass of WebDriverMixin that provides functionality
    to change information for authors. It parses JSON files containing names and surnames,
    and then processes a list of authors to update their names based on the parsed data.
    The class can either make direct changes to the authors' information in a web browser or generate
    JSON files with the changed and unchanged authors.\n
    There are 2 modes:\n
    1) *direct_change* changes info about authors directly on website\n
    2) *changes_in_json* changes info and saves it in json files(result/changed authors.json and result/unchanged authors.json)\n
    *direct_change* also saves info in jsons, that's so because of having to check changed info **manually** to not heck up!\n
    '''

    def __init__(self, email: str, password: str, mode: ChangeMode):
        self._parse_jsons()
        self.mode = mode
        if self.mode == ChangeMode.direct_change:
            super().__init__(email, password)

    def _parse_jsons(self):
        print('Getting names data')
        with open('data/json/names.json') as f:
            data = f.read()
            self.names = set(orjson.loads(data))
        with open('data/json/surnames.json') as f:
            data = f.read()
            self.surnames = set(orjson.loads(data))
        with open('data/blocklist.json') as f:
            data = f.read()
            self.blocklist = set(orjson.loads(data))
        self.names_n_surnames = self.names.union(self.surnames)

    def change_info(self, filepath: str = 'data/authors.json', **kwargs) -> None:
        '''
        The change_info method in the InfoChanger class processes a list of authors and updates their
        names based on parsed data from JSON files. It checks if the author's name can be split into three
        elements and if the names and surnames exist in the parsed data. If the conditions are met, it constructs
        a new name for the author and adds it to the list of changed authors. If any errors occur during the process,
        the author is added to the list of unchanged authors. The method also saves the changed and unchanged authors in
        separate JSON files. If the mode is set to direct_change, it opens tabs in a web browser and updates
        the authors' information on a website.\n
        **Example Usage**\n
        changer = InfoChanger(email='example@example.com', password='password', mode=ChangeMode.direct_change, max_tabs=10)\n
        changer.change_info(filepath='data/authors.json')\n
        **Inputs**\n
        filepath (optional): A string representing the path to the
        JSON file containing the authors' information. Default value is 'data/authors.json'.
        '''
        with open(filepath, 'r') as file:
            authors = orjson.loads(file.read())
        unchanged_authors = list()
        changed_authors = list()
        for author in authors:
            if author['link'] in self.blocklist:
                continue
            fio = [name.title() for name in author.get('name').split()]
            if len(fio) != 3:
                author.update({'error': 'Splitted fullname contains not 3 elements'})
                unchanged_authors.append(author)
                continue
            if len(self.names_n_surnames & set(fio)) != 2:
                author.update({'error': 'No such name/surname in json data!'})
                unchanged_authors.append(author)
                continue
            try:
                surname = self.surnames & set(fio)
                name = self.names & set(fio)
                if len(name) != 1 or len(surname) != 1:
                    raise Exception('Ambiguous fullname!')
                patronymic = set(fio).difference(surname.union(name)).pop()
                name = name.pop()
                surname = surname.pop()
                new_name = f"{surname} {name[0]}. {patronymic[0]}."
                changed_authors.append(
                    {'old_name': author.get('name'), 'new_name': new_name, 'link': author.get('link')})
            except Exception as e:
                author.update({'error': str(e)})
                unchanged_authors.append(author)
                continue
        with open('result/changed authors.json', 'wb') as file:
            file.write(orjson.dumps(changed_authors))
        with open('result/unchanged authors.json', 'wb') as file:
            file.write(orjson.dumps(unchanged_authors))
        if self.mode == ChangeMode.direct_change:
            opened_tabs = 0
            max_tabs = kwargs.get('max_tabs')
            if max_tabs is None:
                max_tabs = 5
            max_tabs = int(max_tabs)
            sleep_time = 5 / max_tabs
            for ca in changed_authors:
                task = ChangeTabInfoTask(self.driver, ca['link'], ca['new_name'])
                task.run()
                opened_tabs += 1
                sleep(sleep_time)
                if opened_tabs >= max_tabs:
                    for _ in range(opened_tabs):
                        self.driver.switch_to.window(self.driver.window_handles[0])
                        self.driver.close()
                        opened_tabs -= 1
                    self.driver.switch_to.window(self.driver.window_handles[-1])

