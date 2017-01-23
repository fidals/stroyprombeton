"""
Create testing DB.

NOTE:
    1. It will purge all the existing data from DB.
    2. It creates random entities, so, tests likely will not pass with new data
    3. It overwrites stroyprombeton/fixtures/dump.json
    4. It can only run if your default database called `test`.
"""
import os

from django.conf import settings
from django.core.files.images import ImageFile
from django.core.management import call_command
from django.core.management.base import BaseCommand

from images.models import Image
from pages.models import CustomPage, FlatPage, ModelPage
from pages.utils import save_custom_pages

from stroyprombeton.models import Product, Category
import stroyprombeton.tests

CATEGORY_PATTERN = 'Category #{} of #{}'
FEEDBACKS_COUNT = 9
REVIEW_IMAGE = os.path.join(
    os.path.dirname(os.path.abspath(stroyprombeton.tests.__file__)),
    'assets/review.jpg'
)


def create_pages():
    def create_regions():
        FlatPage.objects.create(
            name='Empire center state',
            slug='empire-center-state',
            # from settings.CUSTOM_PAGES
            parent=CustomPage.objects.get(slug='regions'),
            position=0,
        )

    def create_news():
        FlatPage.objects.create(
            name='GBI for Krishnas temple',
            slug='krishnas-temple',
            # from settings.CUSTOM_PAGES
            parent=CustomPage.objects.get(slug='news'),
            content='Viktor gave some GBI to Krishnas. Good guy!',
            position=0,
        )

    def create_feedbacks():
        # Start from 1 for `position` instead of 0.
        for i in range(1, FEEDBACKS_COUNT + 1):
            review = FlatPage.objects.create(
                name='"Some company" respect #{}'.format(i),
                # from settings.CUSTOM_PAGES
                parent=CustomPage.objects.get(slug='client-feedbacks'),
                position=i,
            )

            Image.objects.create(
                model=review,
                image=ImageFile(open(REVIEW_IMAGE, mode='rb')),
            )

    save_custom_pages()
    create_regions()
    create_news()
    create_feedbacks()


class Command(BaseCommand):

    @staticmethod
    def purge_tables():
        """Remove everything from Category, Product and Page tables."""
        call_command('flush', '--noinput')

    def handle(self, *args, **options):
        # We need to be sure that this command will run only on 'test' DB.
        assert settings.DATABASES['default']['NAME'] == 'test_stb'

        self._product_id = 0

        self.purge_tables()
        create_pages()
        roots = self.create_root(count=2)
        second_level = self.create_children(count=2, parents=roots)
        third_level = self.create_children(count=2, parents=second_level)
        self.create_products(parents=list(third_level))
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
        get_name = 'Category root #{}'.format
        return [
            Category.objects.create(
                name=get_name(i),
                page=ModelPage.objects.create(name=get_name(i)),
            )
            for i in range(count)
        ]

    @property
    def product_id(self):
        self._product_id += 1
        return self._product_id

    @staticmethod
    def create_children(count, parents):
        def create_category(index, parent):
            name = CATEGORY_PATTERN.format(index, parent.id)
            return Category.objects.create(
                name=name, parent=parent, page=ModelPage.objects.create(name=name))

        return list(
            create_category(index, parent)
            for index in range(count) for parent in parents
        )

    def create_products(self, parents):
        """Create products for every non-root category."""
        def create_products(count, categories):
            for category in categories:
                for i in range(1, count + 1):
                    name = 'Product #{} of {}'.format(i, category)
                    Product.objects.create(
                        id=self.product_id,
                        name=name,
                        price=i * 100,
                        category=category,
                        page=ModelPage.objects.create(name=name)
                    )
        # Create 25 products for
        # tests_selenium.CategoryPage.test_load_more_hidden_in_fully_loaded_categories
        create_products(count=25, categories=parents[4:])
        # Create 50 products for tests_selenium.CategoryPage.test_load_more_products
        create_products(count=50, categories=parents[:4])
