"""
Create testing DB.

NOTE:
    1. It will purge all the existing data from DB.
    2. It creates random entities, so, tests likely will not pass with new data
    3. It overwrites stroyprombeton/fixtures/dump.json
    4. It can only run if your default database called `test`.
"""

from itertools import chain

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand

from pages.models import FlatPage, ModelPage, CustomPage

from stroyprombeton.models import Product, Category


class Command(BaseCommand):

    def handle(self, *args, **options):
        # We need to be sure that this command will run only on 'test' DB.
        assert settings.DATABASES['default']['NAME'] == 'test_stb'

        self._product_id = 0

        self.clear_tables()
        roots = self.create_root(2)
        children = self.create_children(2, roots)
        deep_children = self.create_children(2, children)
        self.create_products(list(deep_children))
        self.create_custom_pages()
        self.create_flat_pages()
        self.save_dump()

    @staticmethod
    def save_dump():
        """Save .json dump to fixtures."""
        call_command(
            'dumpdata',
            '--all',
            '--natural-foreign',
            '--natural-primary',
            output='stroyprombeton/fixtures/dump.json'
        )

    @staticmethod
    def create_root(count):
        get_name = 'Category #{}'.format
        return [
            Category.objects.create(name=get_name(i), page=ModelPage.objects.create(h1=get_name(i)))
            for i in range(count)
        ]

    @property
    def product_id(self):
        self._product_id += 1
        return self._product_id

    @staticmethod
    def create_children(count, parents):
        name = 'Category #{} of #{}'

        def create_categories(name, parent):
            return Category.objects.create(
                name=name, parent=parent, page=ModelPage.objects.create(h1=name))

        def get_name(number, parent=None):
            return name.format(number, parent)

        return chain.from_iterable(
            [
                create_categories(get_name(i, parent), parent)
                for i in range(count)
            ] for parent in parents
        )

    def create_products(self, deep_children):
        """Create products for every non-root category."""
        def create_product(categories, product_count):
            for category in categories:
                for i in range(1, product_count + 1):
                    name = 'Product #{} of {}'.format(i, category)
                    Product.objects.create(
                        id=self.product_id,
                        name=name,
                        price=i * 100,
                        category=category,
                        page=ModelPage.objects.create(h1=name)
                    )
        # Create 25 products for
        # tests_selenium.CategoryPage.test_load_more_hidden_in_fully_loaded_categories
        create_product(deep_children[4:], 25)
        # Create 50 products for tests_selenium.CategoryPage.test_load_more_products
        create_product(deep_children[:4], 50)

    @staticmethod
    def create_custom_pages():
        """Create only one page with type=CUSTOM_TYPE"""
        CustomPage.objects.create(
            slug=''
        )
        CustomPage.objects.create(
            slug='search'
        )
        CustomPage.objects.create(
            slug='gbi'
        )
        CustomPage.objects.create(
            slug='order'
        )
        CustomPage.objects.create(
            slug='news',
        )
        CustomPage.objects.create(
            slug='user-feedbacks',
        )

    @staticmethod
    def create_flat_pages():
        """Create only one page with type=FLAT_PAGE"""
        news = CustomPage.objects.get(slug='news')
        reviews = CustomPage.objects.get(slug='user-feedbacks')

        for i in range(3):
            FlatPage.objects.create(
                h1='News #{}'.format(i),
                parent=news
            )
            FlatPage.objects.create(
                h1='Review #{}'.format(i),
                parent=reviews
            )

    @staticmethod
    def clear_tables():
        """Remove everything from Category, Product and Page tables."""
        call_command('flush', '--noinput')
