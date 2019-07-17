"""Takes catalog data from stalbeton.pro site."""

import typing
from functools import lru_cache
from itertools import chain
from urllib.parse import urljoin

import bs4
import requests
from django.core.management.base import BaseCommand


class ThroughElements:
    """Such elements are presented on every page. Header and footer for example."""

    def __init__(self, page: 'Page'):
        self.page = page

    def roots(self) -> typing.List['RootCategoryPage']:
        roots = self.page.soup.select('.catalog-tabs-content__list .catalog-list__link')
        assert roots
        return [RootCategoryPage(path=r['href']) for r in roots]

    def work_doc(self) -> typing.List['CategoryPage']:
        # @todo #741:30m  Parse work docs from stalbeton.
        #  Don't create series entity. It's for another task.
        raise NotImplemented()


class Page:
    SITE_URL = 'https://stalbeton.pro'

    def __init__(self, path: str):
        # '/catalog/dorozhnoe-stroitelstvo' for example
        self.path = path

    @property
    def url(self) -> str:
        return urljoin(self.SITE_URL.strip('/'), self.path.strip('/'))

    @property
    @lru_cache(maxsize=1)
    def page(self) -> requests.Response:
        response = requests.get(self.url)
        assert response.status_code == 200, self
        return response

    @property
    @lru_cache(maxsize=1)
    def soup(self) -> bs4.BeautifulSoup:
        return bs4.BeautifulSoup(
            self.page.content.decode('utf-8'),
            'html.parser'
        )

    def __str__(self):
        return self.path

    @property
    def title(self) -> str:
        return self.soup.find('title').text

    @property
    def h1(self) -> str:
        return self.soup.find('h1').text

    @property
    def description(self) -> str:
        return self.soup.select_one('meta[name="Description"]')['content']


class CategoryPage(Page):
    @property
    def text(self) -> str:
        """
        Only category page has unique text.

        Every another text has autogenerated content.
        """
        return self.soup.select_one('#js-category-description').text


class RootCategoryPage(CategoryPage):
    # @todo #741:30m  Implement parse_stalbeton.Category.children() method.
    #  And reuse it as polymorphic method in subclasses.
    #  The task has pros and cons, so, we'll discuss it for the first.
    def second_level(self) -> typing.List['SecondLevelCategoryPage']:
        return [
            SecondLevelCategoryPage(p['href'])
            for p in self.soup.select('h2 > a.catalog-list__link')
        ]


class SecondLevelCategoryPage(CategoryPage):
    def third_level(self) -> typing.List['ThirdLevelCategoryPage']:
        return [
            ThirdLevelCategoryPage(p['href'])
            for p in self.soup.select('h2 > a.catalog-list__link')
        ]


class PageElement:
    def __init__(self, soup: bs4.element.Tag):
        self.soup = soup


# @todo #761:60m  Implement parse_stalbeton.Properties class.
#  It full name is `OptionPropertiesSet`.
#  We can extract property dimensions only from html tag class names.
#  For ex the same property Length can have
#  either 'unit_length_mm' or 'unit_length_m' class name.
class OptionPropertiesSet(PageElement):
    @property
    def length(self) -> typing.Union[float, None]:
        raise NotImplemented()

    @property
    def width(self) -> typing.Union[float, None]:
        raise NotImplemented()

    @property
    def height(self) -> typing.Union[float, None]:
        raise NotImplemented()

    @property
    def diameter_out(self) -> typing.Union[float, None]:
        raise NotImplemented()

    @property
    def diameter_in(self) -> typing.Union[float, None]:
        raise NotImplemented()

    @property
    def volume(self) -> typing.Union[float, None]:
        raise NotImplemented()

    @property
    def mass(self) -> typing.Union[int, None]:
        raise NotImplemented()


class Option(PageElement):
    @property
    def path(self) -> str:
        return self.soup.find(class_='link_theme-line')['href']

    @property
    def name(self) -> str:
        return self.soup.find(class_='link_theme-line').text

    @property
    def product_name(self) -> str:
        return self.soup.find(class_='product-info-caption__item').text

    @property
    def series(self) -> str:
        return self.soup.find(class_='product-info-caption__link').text

    @property
    def price(self) -> typing.Union[int, None]:
        text = self.soup.find(class_='unit_price').text.replace(' ', '')
        # input text can't be float number
        return int(text) if text.isnumeric() else None

    def options(self) -> OptionPropertiesSet:
        return OptionPropertiesSet(self.soup.find(class_='product-info-param'))


class ThirdLevelCategoryPage(CategoryPage):
    def options(self) -> typing.List[Option]:
        return [
            Option(soup)
            for soup in self.soup.select('.product-grid-list-item')
        ]

    # @todo #741:60m Parse series from stalbeton.
    #  Series are already parsed as text strings.
    #  Parse them as separated pages to get options-series relation.
    def series(self) -> typing.List[str]:
        return [
            item.text for item in self.soup.select(
                '.documentation-block span.documentation-block__item > a'
            )
        ]


def parse():
    main = Page(path='/')
    through = ThroughElements(page=main)
    roots = through.roots()
    # @todo #741:30m  Create parse_stalbeton.Categories class.
    #  And hide children list assembling there.
    #  See PR #758 discussion for example.
    seconds = chain.from_iterable((r.second_level() for r in roots))
    thirds = chain.from_iterable((s.third_level() for s in seconds))
    options = chain.from_iterable((t.options() for t in thirds))  # Ignore PyFlakesBear
    # @todo #741:60m Save parsed stalbeton to a DB.
    #  DB isn't required to be high performance.
    #  It can be sqlite or postgres or pickle lib or whatever else.
    #  DB is required to analyze data without loading stalbeton site every time.


class Command(BaseCommand):
    def handle(self, *args, **options):
        parse()
