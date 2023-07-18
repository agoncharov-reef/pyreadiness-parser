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
    @limits(calls=1, period=4)
    def get_language_ratio(self) -> dict[str, float]:

        links = self.get_info()['info']['project_urls']
        try:
            github_url = one({url for url in links.values() if url.startswith('https://github.com') and url.count('/') == 4})
        except ValueError:
            log.warning('Cannot detect github url for %s: %s', self.name, links)
            return {}

        owner, repo = github_url.removeprefix('https://github.com/').split('/')
        response = session.get(f'https://api.github.com/repos/{owner}/{repo}/languages')
        response.raise_for_status()
        languages = response.json()

        total = sum(languages.values())
        return {language: value/total for language, value in languages.items()}


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
                ' '.join(f'{language}:{value*100:.2f}%' for language, value in project.get_language_ratio().items()),
            ) for project in tqdm(parse_pyreadiness())
        ],
        headers=('rating', 'ready', 'name', 'url', 'languages'),
    ))
