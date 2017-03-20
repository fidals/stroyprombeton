import os

from xml.etree import ElementTree

from django.conf import settings
from django.test import TestCase

from pages.models import Page

from django.core.management import call_command
from stroyprombeton.management.commands.seo_texts import populate_entities


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

    def test_removed_files(self):
        """After performing command there should be no files."""
        self.assertNotIn('yandex.yml', os.listdir(settings.BASE_DIR))

    def test_price_exists(self):
        """`Catalog` command should generate non empty files."""
        price_file_min_size = 10 ** 4  # ~10kb

        for pricelist in self.PRICE_FILES:
            file_name = self.get_price_file_path(pricelist)
            self.assertIn(pricelist, os.listdir(settings.ASSETS_DIR))

            size = os.stat(file_name).st_size
            self.assertGreaterEqual(size, price_file_min_size)

    def test_shop_info(self):
        """There should be correct information about site in pricelist."""
        site_name = self.pricelist_body.find('name').text
        self.assertTrue(site_name, 'Stroyprombeton')

        company_name = self.pricelist_body.find('company').text
        self.assertTrue(company_name, 'Stroyprombeton')

        site_url = self.pricelist_body.find('url').text
        self.assertTrue(site_url, settings.BASE_URL)

        site_email = self.pricelist_body.find('email').text
        self.assertTrue(site_email, settings.SHOP_EMAIL)

        site_cpa = self.pricelist_body.find('cpa').text
        self.assertTrue(site_cpa, 0)

    def test_categories_in_price(self):
        """There should be at least 500 categories in Pricelist."""
        categories_in_price = self.pricelist_body.find('categories')
        self.assertGreaterEqual(len(categories_in_price), 500)

    def test_products_in_price(self):
        """There should be at least 9000 products in Pricelist."""
        products_in_price = self.pricelist_body.find('offers')
        self.assertGreaterEqual(len(products_in_price), 9000)


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
