from collections import Counter
import logging
from dataclasses import dataclass, asdict
from itertools import count
from typing import Iterator

import requests
from bs4 import BeautifulSoup
from more_itertools import one
from ratelimit import limits
from ratelimit.exception import RateLimitException
from tabulate import tabulate
from tenacity import retry, retry_if_exception_type, wait_fixed
from tqdm import tqdm

session = requests.Session()
log = logging.getLogger()


def get_owner_and_project(github_url: str) -> tuple[str, str]:
    owner, project, *_ = github_url.removeprefix('https://github.com/').split('/')
    return owner, project


@dataclass
class PypiProject:
    name: str
    rating: int
    is_ready: bool

    @property
    def url(self) -> str:
        return f'https://pypi.org/project/{self.name}'

    def __str__(self) -> str:
        return self.name

    def get_info(self) -> dict:
        response = session.get(f'https://pypi.org/pypi/{self.name}/json')
        response.raise_for_status()
        return response.json()

    @retry(
        wait=wait_fixed(1),
        retry=retry_if_exception_type(RateLimitException),
    )
    @limits(calls=1, period=3)
    def get_language_ratio_precise(self) -> dict[str, float]:

        links = self.get_info()['info']['project_urls']
        github_urls = {url for url in links.values() if url.startswith('https://github.com')}

        try:
            owner, project = Counter(get_owner_and_project(url) for url in github_urls).most_common(1)[0][0]
        except IndexError:
            log.warning('Could not detect github owner and project for "%s": %s', self.name, links)
            return {}

        response = session.get(f'https://api.github.com/repos/{owner}/{project}/languages')
        response.raise_for_status()
        languages = response.json()

        total = sum(languages.values())
        return {language: value/total for language, value in languages.items()}

    def get_language_ratio_approximate(self) -> dict[str, float]:

        links = self.get_info()['info']['project_urls'] or {}

        urls = {url.replace('http://', 'https://') for url in links.values()}
        github_urls = {url for url in urls if url.startswith('https://github.com')}

        try:
            owner, project = Counter(get_owner_and_project(url) for url in github_urls).most_common(1)[0][0]
        except IndexError:
            log.warning('Could not detect github owner and project for "%s": %s', self.name, links)
            return {}

        response = session.get(f'https://github.com/{owner}/{project}')
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        try:
            languages = soup.find('h2', string='Languages').parent
            value = languages.find('span', string='Python').find_next_sibling('span').text.strip()
            return {'Python': float(value.removesuffix('%'))/100}
        except AttributeError:
            return {}

        result = {}
        for language in languages:
            spans = language.findAll('span')
            assert len(spans) == 2, f'Expected 2 spans, got {len(spans)}: {spans} ({self.name})'

            name = spans[0].text.strip()
            value = float(spans[1].text.strip().removesuffix('%'))/100
            result[name] = value

        return result


def parse_pyreadiness(version: str = '3.11') -> Iterator[PypiProject]:
    response = session.get(f'https://pyreadiness.org/{version}')
    response.raise_for_status()

    counter = count()
    soup = BeautifulSoup(response.text, 'html.parser')
    lists = soup.find_all('div', class_='list')
    for list_ in lists:
        projects = list_.find_all('a')
        for project in projects:
            name, sign = project.text.strip().split(' ')
            yield PypiProject(
                name=name,
                rating=next(counter),
                is_ready=sign == '✓',
            )


if __name__ == '__main__':
    print(tabulate(
        [
            (
                project.rating,
                '+' if project.is_ready else '-',
                project.name,
                project.url,
                ' '.join(f'{language}:{value*100:.2f}%' for language, value in project.get_language_ratio_approximate().items()),
            ) for project in tqdm(parse_pyreadiness())
        ],
        headers=('rating', 'ready', 'name', 'url', 'languages'),
    ))
