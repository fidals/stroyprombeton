import os
from xml.etree import ElementTree

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase, tag

from pages.models import Page
from stroyprombeton.management.commands.seo_texts import populate_entities
from stroyprombeton.models import Option, Product


@tag('fast')
class ImportTest(TestCase):

    PRICE_FILES = ['yandex.yml']

    @classmethod
    def setUpTestData(cls):
        call_command('price')

        cls.pricelist_body = (
            ElementTree.parse(ImportTest.get_price_file_path('yandex.yml')).getroot().find('shop')
        )

    @staticmethod
    def get_price_file_path(filename):
        return os.path.join(settings.ASSETS_DIR, filename)

    @classmethod
    def tearDownClass(cls):
        super(ImportTest, cls).tearDownClass()
        for file_name in cls.PRICE_FILES:
            os.remove(ImportTest.get_price_file_path(file_name))

    def test_yandex_import(self):
        """`price` command should generate non empty files."""
        for pricelist in self.PRICE_FILES:
            file_name = self.get_price_file_path(pricelist)
            self.assertIn(pricelist, os.listdir(settings.ASSETS_DIR))

            size = os.stat(file_name).st_size
            self.assertGreaterEqual(size, 1)

        """There should be correct information about site in pricelist."""
        site_name = self.pricelist_body.find('name').text
        self.assertTrue(site_name, 'Stroyprombeton')

        company_name = self.pricelist_body.find('company').text
        self.assertTrue(company_name, 'Stroyprombeton')

        site_url = self.pricelist_body.find('url').text
        self.assertTrue(site_url, settings.BASE_URL)

        site_email = self.pricelist_body.find('email').text
        self.assertTrue(site_email, settings.EMAIL_RECIPIENTS)

        site_cpa = self.pricelist_body.find('cpa').text
        self.assertTrue(site_cpa, 0)


@tag('fast')
class SeoTexts(TestCase):

    setting = {
        'populate_model': Page,
        'populate_fields': {},
    }

    def setUp(self):
        self.first_page = Page.objects.create(name='First', content='Just q')
        self.second_page = Page.objects.create(name='Second')

    def tearDown(self):
        self.first_page.delete()
        self.second_page.delete()

    def test_populate_entities_by_template(self):
        first_page_content = self.first_page.content
        second_page_content = self.second_page.content

        self.setting.update(populate_fields={
            'content': {'template': {'text': 'It is {}', 'variables': ['name']}}
        })

        populate_entities(**self.setting)

        self.setting.update(populate_fields={})

        test_first_page_content = Page.objects.get(name=self.first_page.name).content
        test_second_page_content = Page.objects.get(name=self.second_page.name).content

        self.assertEqual(first_page_content, test_first_page_content)
        self.assertNotEqual(second_page_content, test_second_page_content)


@tag('fast')
class RemoveDuplicates(TestCase):

    fixtures = ['dump.json']

    def test_keep_unsimilar_options(self):
        product = Product.objects.first()
        options = list(product.options.all())
        call_command(
            'remove_option_duplicates',
            'mark', 'product',
            noinput='true',
        )
        self.assertEqual(options, list(product.options.all()))

    def test_remove_similar_options(self):
        product = Product.objects.first()

        count = 3
        group_count = 2
        total = count * group_count + len(product.options.all())
        codes = ['123' * i for i in range(1, group_count + 1)]

        for code in codes:
            Option.objects.bulk_create([
                Option(mark=f'mark #{i}', code=code, product=product)
                for i in range(count)
            ])
        self.assertEqual(product.options.count(), total)

        # remove one option from each group of similar options by code and product
        call_command(
            'remove_option_duplicates',
            'code', 'product',
            noinput='true',
        )
        for code in codes:
            self.assertEqual(
                product.options.filter(code=code).count(),
                count - 1,
            )
