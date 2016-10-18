"""
Views tests.

Note: there should be tests, subclassed from TestCase.
They all should be using Django's TestClient.

All Selenium-tests should be located in tests_selenium.
"""
from copy import copy
from datetime import datetime

from django.test import TestCase

from pages.models import Page
from stroyprombeton.management.commands.transfer import custom_page_data
from stroyprombeton.models import Category, Product
from stroyprombeton.tests.tests_forms import PriceFormTest, DrawingFormTest


def create_custom_pages():
    """Create index, category_tree, news and region pages."""
    for fields in custom_page_data.values():
        Page.objects.create(**fields)


class CategoryTree(TestCase):
    """Tests for CategoryTree view """

    @classmethod
    def setUpTestData(cls):
        """Create root and child category."""
        create_custom_pages()
        cls.root_name = 'Test root category'
        cls.child_name = 'Test child category'

        root_category = Category.objects.create(
            name=cls.root_name
        )

        Category.objects.create(
            name=cls.child_name,
            parent=root_category
        )

    def setUp(self):
        """Get response from /gbi/"""
        self.response = self.client.get('/gbi/')

    def test_response_status_code(self):
        status_code = self.response.status_code

        self.assertEqual(status_code, 200)

    def test_root_catalog_name(self):
        """Test """
        name = self.response.context['nodes'][0].name

        self.assertEqual(name, self.root_name)

    def test_child_catalog_name(self):
        name = self.response.context['nodes'][1].name

        self.assertEqual(name, self.child_name)

    def test_catalogs_quantity(self):
        quantity = len(self.response.context['nodes'])

        self.assertEqual(quantity, 2)


class CategoryTile(TestCase):
    """Test for CategoryPage view under the condition,that using CategoryTile
    template."""

    @classmethod
    def setUpTestData(cls):
        """Create root and child category."""
        create_custom_pages()
        cls.root_data = {
            'name': 'Test root category',
            'id': 1,
            'page': Page.objects.create(
                content='Козырьки устанавливают над входами зданий.',
                h1='Козырьки',
            ),
        }

        cls.root_category = Category.objects.create(**cls.root_data)

        cls.child_data = {
            'name': 'Test child category',
            'id': 2,
            'parent': cls.root_category,
            'page': Page.objects.create(
                content='Козырьки применяют при строительстве зданий.',
                h1='Козырьки входов, плиты парапетные.',
            )
        }

        Category.objects.create(**cls.child_data)

    def setUp(self):
        """Get response from /gbi/categories/1/"""
        self.response = self.client.get('/gbi/categories/' + str(self.root_data['id']) + '/')

    def test_response_status_code(self):
        status_code = self.response.status_code

        self.assertEqual(status_code, 200)

    def test_page(self):
        page = self.response.context['page']

        self.assertTrue(page)

    def test_h1(self):
        h1 = self.response.context['category'].page.h1

        self.assertEqual(h1, self.root_data['page'].h1)

    def test_content(self):
        content = self.response.context['page'].content

        self.assertEqual(content, self.root_data['page'].content)

    def test_children_categories_quantity(self):
        quantity = len(self.response.context['children'])

        self.assertEqual(quantity, 1)

    def test_children_category_name(self):
        name = self.response.context['children'][0].name

        self.assertEqual(name, self.child_data['name'])


class CategoryTable(TestCase):
    """Test for CategoryPage view under the condition, that using CategoryTable
    template."""

    @classmethod
    def setUpTestData(cls):
        """Create category and product."""
        create_custom_pages()
        cls.root_data = {
            'name': 'Test root category',
            'id': 1,
            'page': Page.objects.create(
                h1='Козырьки',
                content='Козырьки устанавливают над входами зданий.',
            )
        }

        root_category = Category.objects.create(**cls.root_data)

        cls.product_data = {
            'price': 1447.21,
            'code': 350,
            'name': 'Test product name',
            'date_price_updated': datetime.now(),
            'category': root_category
        }

        Product.objects.create(**cls.product_data)

    def setUp(self):
        """Get response from /gbi/categories/1/"""
        self.response = self.client.get('/gbi/categories/1/')

    def test_response_status_code(self):
        status_code = self.response.status_code

        self.assertEqual(status_code, 200)

    def test_page(self):
        page = self.response.context['page']

        self.assertTrue(page)

    def test_h1(self):
        h1 = self.response.context['page'].h1

        self.assertEqual(h1, self.root_data['page'].h1)

    def test_content(self):
        content = self.response.context['page'].content

        self.assertEqual(content, self.root_data['page'].content)

    def test_products_quantity(self):
        quantity = len(self.response.context['products'])

        self.assertEqual(quantity, 1)

    def test_product_name(self):
        name = self.response.context['products'][0].name

        self.assertEqual(name, self.product_data['name'])

    def test_product_price(self):
        price = float(self.response.context['products'][0].price)

        self.assertEqual(price, self.product_data['price'])

    def test_product_code(self):
        code = self.response.context['products'][0].code

        self.assertEqual(code, self.product_data['code'])


class Product_(TestCase):
    """Test for ProductPage view."""

    @classmethod
    def setUpTestData(cls):
        """Create category and product."""
        create_custom_pages()
        root_data = {
            'id': 1,
            'name': 'Test root category',
        }

        root_category = Category.objects.create(**root_data)

        cls.product_data = {
            'id': 1,
            'category': root_category,
            'name': 'Test product name',
            'price': 1447.21,
            'code': 350,
            'mark': 350,
            'specification': 'Серия 1.238-1-1',
            'length': 12345,
            'width': 12456,
            'height': 1234,
            'diameter_in': 123,
            'diameter_out': 321,
            'weight': 1111,
            'volume': 2222,
            'date_price_updated': datetime.now(),
            'page': Page.objects.create(
                content='Козырьки устанавливают над входами зданий.',
                h1='Козырьки',
            )
        }

        Product.objects.create(**cls.product_data)

    def setUp(self):
        self.response = self.client.get('/gbi/products/1/')

    def test_response_status_code(self):
        status_code = self.response.status_code

        self.assertEqual(status_code, 200)

    def test_page(self):
        page = self.response.context['page']

        self.assertTrue(page)

    def test_h1(self):
        h1 = self.response.context['page'].h1

        self.assertEqual(h1, self.product_data['page'].h1)

    def test_product_name(self):
        name = self.response.context['product'].name

        self.assertEqual(name, self.product_data['name'])

    def test_product_price(self):
        price = float(self.response.context['product'].price)

        self.assertEqual(price, self.product_data['price'])

    def test_product_code(self):
        code = self.response.context['product'].code

        self.assertEqual(code, self.product_data['code'])

    def test_product_mark(self):
        mark = int(self.response.context['product'].mark)

        self.assertEqual(mark, self.product_data['mark'])

    def test_product_length(self):
        length = self.response.context['product'].length

        self.assertEqual(length, self.product_data['length'])

    def test_product_width(self):
        width = self.response.context['product'].width

        self.assertEqual(width, self.product_data['width'])

    def test_product_height(self):
        height = self.response.context['product'].height

        self.assertEqual(height, self.product_data['height'])

    def test_product_diameter_in(self):
        diameter_in = self.response.context['product'].diameter_in

        self.assertEqual(diameter_in, self.product_data['diameter_in'])

    def test_product_diameter_out(self):
        diameter_out = self.response.context['product'].diameter_out

        self.assertEqual(diameter_out, self.product_data['diameter_out'])

    def test_product_weight(self):
        weight = self.response.context['product'].weight

        self.assertEqual(weight, self.product_data['weight'])

    def test_product_volume(self):
        volume = self.response.context['product'].volume

        self.assertEqual(volume, self.product_data['volume'])

    def test_product_specification(self):
        specification = self.response.context['product'].specification

        self.assertEqual(specification, self.product_data['specification'])


class AbstractFormViewTest:
    """
    Define common test cases for views with Forms.

    Subclasses should also inherit TestCase!
    """
    URL = ''
    SUCCESS_URL = ''
    FORM_TEST = None
    FIELDS = []

    def setUp(self):
        self.response = self.client.get(self.URL)

    def test_response_status_code(self):
        status_code = self.response.status_code

        self.assertEqual(status_code, 200)

    def test_submit_form(self):
        response = self.client.post(self.URL, self.FIELDS)
        self.assertRedirects(response, self.SUCCESS_URL)

    def test_submit_form_without_required(self):
        wrong_fields = {'name': 'Test'}
        response = self.client.post(self.URL, wrong_fields)
        for required_field in self.FORM_TEST.REQUIRED:
            self.assertFormError(response, 'form', required_field,
                                 ['This field is required.'])

    def test_submit_invalid_email(self):
        wrong_fields = {'email': 'non@a/em.il'}
        response = self.client.post(self.URL, wrong_fields)
        self.assertFormError(response, 'form', 'email',
                             ['Enter a valid email address.'])


class OrderPrice(AbstractFormViewTest, TestCase):
    URL = '/order-price/'
    SUCCESS_URL = '/price-success/'
    FORM_TEST = PriceFormTest
    FIELDS = copy(PriceFormTest.FIELDS)


class OrderDrawing(AbstractFormViewTest, TestCase):
    URL = '/order-drawing/'
    SUCCESS_URL = '/drawing-success/'
    FORM_TEST = DrawingFormTest
    FIELDS = copy(DrawingFormTest.FIELDS)
