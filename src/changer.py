from time import sleep
import re

import orjson
from loguru import logger

from src.base import WebDriverMixin, ChangeMode
from src.tab import ChangeTabInfoTask


class ChangerException(Exception):
    ...


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
        logger.info('Scraping jsons with all names and surnames')
        with open('data/json/names.json') as f:
            data = f.read()
            self.names = set(orjson.loads(data))
        with open('data/json/surnames.json') as f:
            data = f.read()
            self.surnames = set(orjson.loads(data))
        with open('data/blocklist.json') as f:
            data = f.read()
            self.blocklist = set(orjson.loads(data))

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
        logger.debug(f"Started changing with mode: '{self.mode.name}'")
        with open(filepath, 'r') as file:
            authors = orjson.loads(file.read())
        unchanged_info = list()
        changed_info = list()
        already_correct = 0
        for author in authors:
            if author['link'] in self.blocklist:
                continue
            fio = [name.title() for name in author.get('name').split()]
            try:
                initials = re.findall(r'[А-ЯЁ]\.', author['name'])
                if len(initials) == 2:
                    surname = self.surnames & set(fio)
                    new_name = f"{surname.pop()} {initials[0]} {initials[1]}"
                    if author['name'] == new_name:
                        raise ChangerException('Author already has correct fullname.')
                    changed_info.append(
                        {'old_name': author.get('name'), 'new_name': new_name, 'link': author.get('link')})
                    continue
                if len(fio) != 3:
                    raise ChangerException('Splitted fullname contains not 3 elements.')
                surname = self.surnames & set(fio)
                name = self.names & set(fio)
                if not(len(name) and len(surname)):
                    raise ChangerException('No such surname or name in data.')
                if len(name) != 1 or len(surname) != 1:
                    raise ChangerException('Ambiguous fullname.')
                patronymic = set(fio).difference(surname.union(name)).pop()
                name = name.pop()
                surname = surname.pop()
                new_name = f"{surname} {name} {patronymic}"
                if author['name'] == new_name:
                    already_correct.append(author)
                changed_info.append(
                    {'old_name': author.get('name'), 'new_name': new_name, 'link': author.get('link')})
            except Exception as e:
                author.update({'error': str(e)})
                unchanged_info.append(author)
                continue

        logger.info('Parsing changed info into jsons')
        with open('result/changed info.json', 'wb') as file:
            file.write(orjson.dumps(changed_info))
        with open('result/unchanged info.json', 'wb') as file:
            file.write(orjson.dumps(unchanged_info))
        logger.debug(f"{len(changed_info)} authors were parsed to file 'changed info.json'")
        logger.debug(f"{len(unchanged_info)} authors were parsed to file 'unchanged info.json'")
        if self.mode == ChangeMode.direct_change:
            updated_authors = list()
            try:
                opened_tabs = 0
                max_tabs = kwargs.get('max_tabs')
                if max_tabs is None:
                    max_tabs = 10
                max_tabs = int(max_tabs)
                sleep_time = 3 / max_tabs
                for ca in changed_info:
                    task = ChangeTabInfoTask(self.driver, ca['link'], ca['new_name'])
                    task.run()
                    opened_tabs += 1
                    sleep(sleep_time)
                    updated_authors.append(ca)
                    if opened_tabs >= max_tabs:
                        for _ in range(opened_tabs):
                            self.driver.switch_to.window(self.driver.window_handles[0])
                            self.driver.close()
                            opened_tabs -= 1
                        self.driver.switch_to.window(self.driver.window_handles[-1])
            except:
                logger.warning('Error occured while direct updating authors!')
            logger.info('Parsing authors that was updated in json')
            with open('result/updated authors.json', 'wb') as file:
                file.write(orjson.dumps(updated_authors))
            logger.debug(f"{len(updated_authors)} were updated and parsed in 'updated authors.json'")

