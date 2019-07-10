"""Takes catalog data from stalbeton.pro site."""

import typing
from itertools import chain
from urllib.parse import urljoin

import bs4
import requests
from django.core.management.base import BaseCommand


class Page:
    SITE_URL = 'https://stalbeton.pro'
    path = '/'

    def url(self) -> str:
        return urljoin([self.SITE_URL.strip('/'), self.path.strip('/')])

    def get_page(self) -> requests.Response:
        return requests.get(self.url())

    def get_soup(self) -> bs4.BeautifulSoup:
        return bs4.BeautifulSoup(
            self.get_page().content.decode('utf-8'),
            'html.parser'
        )

    def title(self) -> str:
        raise NotImplemented()

    def h1(self) -> str:
        raise NotImplemented()

    def keywords(self) -> str:
        raise NotImplemented()

    def description(self) -> str:
        raise NotImplemented()


class CategoryPage(Page):
    def __init__(self, path: str):
        # '/catalog/dorozhnoe-stroitelstvo' for example
        self.path = path


class ThroughElements(Page):
    """Such elements are presented on every page. Header and footer for example."""

    def work_doc(self) -> typing.List[CategoryPage]:
        # parse work doc categories
        pass


class CatalogPage(Page):
    path = 'catalog'

    def roots(self) -> typing.List['RootCategoryPage']:
        # parse root categories
        pass

    def second_level(self) -> typing.List['SecondLevelCategoryPage']:
        # parse second level categories
        pass


class RootCategoryPage(CategoryPage):
    pass


class SecondLevelCategoryPage(CategoryPage):
    def third_level(self) -> typing.List['ThirdLevelCategoryPage']:
        # parse it
        pass


class ThirdLevelCategoryPage(CategoryPage):
    def options(self) -> list:
        # parse it
        pass


# @todo #736:120m  Parse stalbeton pages.
#  See "parse it" comments inside the classes.
def parse():
    # @todo #736:60m  Try to use stalbeton sitemap.xml.
    #  To get all category links. If you'll be succeed, use it
    #  instead of nested category parsing, drafted with the code below.
    roots = CatalogPage().roots()  # Ignore PyFlakesBear
    second_level = CatalogPage().second_level()
    third_level = chain.from_iterable((s.third_level() for s in second_level))
    options = chain.from_iterable((t.options() for t in third_level))  # Ignore PyFlakesBear
    # save it into our DB


class Command(BaseCommand):
    def handle(self, *args, **options):
        parse()
