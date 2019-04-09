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
from pages.models import CustomPage, FlatPage, ModelPage, Page, PageTemplate
from pages.utils import save_custom_pages
from stroyprombeton import models as stb_models, tests as stb_tests

TEST_DB = 'test_stb'

# use empty roots to feel how UI looks like.
REAL_ROOTS_COUNT = 2
EMPTY_ROOTS_COUNT = 38
ROOT_PATTERN = 'Category root #{}'
EMPTY_ROOT_PATTERN = 'Category root empty #{}'

CATEGORY_PATTERN = 'Category #{} of #{}'
FEEDBACKS_COUNT = 9
REVIEW_IMAGE = os.path.join(
    os.path.dirname(os.path.abspath(stb_tests.__file__)),
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
                name=f'"Some company" respect #{i}',
                # from settings.CUSTOM_PAGES
                parent=CustomPage.objects.get(slug='client-feedbacks'),
                position=i,
            )

            # @todo #296:60m Test image uploading with admin panel.
            Image.objects.create(
                model=review,
                image=ImageFile(open(REVIEW_IMAGE, mode='rb')),
            )

    save_custom_pages()
    create_regions()
    create_news()
    create_feedbacks()


class Command(BaseCommand):

    FIRST_IMAGE = os.path.join(
        os.path.dirname(os.path.abspath(stb_tests.__file__)),
        'assets/deer.jpg'
    )
    SECOND_IMAGE = os.path.join(
        os.path.dirname(os.path.abspath(stb_tests.__file__)),
        'assets/gold_deer.jpg'
    )

    # prod#110 is the first on the root category.
    # prod#92 is the first in the root categories load_more list
    PRODUCTS_WITH_IMAGE = [110, 92]

    def __init__(self):
        super().__init__()
        self._product_id = 0
        self.group_names = [
            'Длина', 'Масса',
        ]
        self.tag_names = [
            ['1 м', '2 м'],
            ['2 кг', '3 кг'],
            ['72 %', '146 %'],
        ]

    @staticmethod
    def purge_tables():
        """Remove everything from models.Category., Product and Page tables."""
        call_command('flush', '--noinput')

    def handle(self, *args, **options):
        self.prepare_db()

        roots = self.create_root()
        second_level = self.create_children(count=2, parents=roots)
        third_level = self.create_children(count=2, parents=second_level)

        groups = self.create_tag_groups()
        tags = self.create_tags(groups)

        create_pages()
        self.create_products(parents=list(third_level), tags=tags)
        self.create_templates()
        self.save_dump()

    def prepare_db(self):
        is_test_db = settings.DATABASES['default']['NAME'] == TEST_DB
        assert is_test_db, \
            f'To create fixtures you have to create a database named "{TEST_DB}".'
        call_command('migrate')
        self.purge_tables()

    @staticmethod
    def save_dump():
        """Save .json dump to fixtures."""
        call_command(
            'dumpdata',
            '--all',
            '--natural-foreign',
            '--natural-primary',
            '-e',
            'sites',
            output='stroyprombeton/fixtures/dump.json'
        )

    @staticmethod
    def create_root():
        def create_category(id: int, pattern: str):
            return stb_models.Category.objects.create(
                name=pattern.format(id),
                page=ModelPage.objects.create(name=pattern.format(id)),
            )

        real_roots = [
            create_category(id=i, pattern=ROOT_PATTERN)
            for i in range(REAL_ROOTS_COUNT)
        ]
        for i in range(EMPTY_ROOTS_COUNT):
            create_category(id=i, pattern=EMPTY_ROOT_PATTERN)
        # return only real roots, because only they should have children
        return real_roots

    def create_tag_groups(self):
        for i, name in enumerate(self.group_names, start=1):
            yield stb_models.TagGroup.objects.create(
                name=name,
                position=i,
            )

    def create_tags(self, groups):
        def create_tag(group_, position, name):
            return stb_models.Tag.objects.create(
                group=group_,
                name=name,
                position=position,
            )

        for group, names in zip(groups, self.tag_names):
            yield [
                create_tag(group, i, name)
                for i, name in enumerate(names, start=1)
            ]

    @staticmethod
    def create_templates():
        page_template = PageTemplate.objects.create(
            name='{{ page.name }} name.',
            h1='{{ page.name }}{{ tag_titles }} h1.',
            keywords='{{ page.name }} keywords.',
            description='{{ page.name }} description.',
            title='{{ page.name }} title.',
            seo_text=(
                '{{ page.name }} seotext.'
                '{% for tag in tags %}{{ tag.name }}, {% endfor %}'
            )
        )

        stb_models.ProductPage.objects.update(template=page_template)
        stb_models.CategoryPage.objects.update(template=page_template)

    @property
    def product_id(self):
        self._product_id += 1
        return self._product_id

    @staticmethod
    def create_children(count, parents):
        def create_category(index, parent):
            name = CATEGORY_PATTERN.format(index, parent.id)
            return stb_models.Category.objects.create(
                name=name, parent=parent, page=ModelPage.objects.create(name=name))

        return list(
            create_category(index, parent)
            for index in range(count) for parent in parents
        )

    def create_products(self, parents, tags):
        """Create products for every non-root category."""
        def create_images(page: Page):
            def create_image(file_path, slug):
                # save files to media folder
                with open(file_path, mode='rb') as file_src:
                    # product "/catalog/products/2/" contains image
                    Image.objects.create(
                        model=page,
                        slug=slug,
                        image=ImageFile(file_src)
                    )

            create_image(file_path=self.FIRST_IMAGE, slug='deer')
            create_image(file_path=self.SECOND_IMAGE, slug='gold')

        def create_products(count, categories, tags_):
            for category in categories:
                for i in range(1, count + 1):
                    name = f'Product #{i} of {category}'
                    product = stb_models.Product.objects.create(
                        id=self.product_id,
                        name=name,
                        category=category,
                        page=ModelPage.objects.create(name=name),
                        # remove this in favor Option
                    )
                    option = stb_models.Option.objects.create(
                        price=i * 100,
                        mark=f'mark #{i}',
                        product=product,
                    )
                    for tag in tags_:
                        option.tags.add(tag)
                        option.save()

                    if product.id in self.PRODUCTS_WITH_IMAGE:
                        create_images(product.page)

        # [('1 м', '2 кг', '72 %'), ('2 м', '3 кг', '146 %')]
        zipped_tags = list(zip(*tags))
        # Create 25 products for
        # tests_selenium.models.Category.Page.test_load_more_hidden_in_fully_loaded_categories
        create_products(count=25, categories=parents[5:], tags_=zipped_tags[0])
        # some products should not contain any tag
        create_products(count=25, categories=parents[4:5], tags_=[])
        # Create 50 products for tests_selenium.models.Category.Page.test_load_more_products
        create_products(count=50, categories=parents[:4], tags_=zipped_tags[1])
