"""
Views tests.

Note: there should be tests, subclassed from TestCase.
They all should be using Django's TestClient.

All Selenium-tests should be located in tests_selenium.
"""
from copy import copy
from datetime import datetime

from django.http import QueryDict
from django.test import TestCase, override_settings
from django.urls import reverse

from pages.models import CustomPage, FlatPage, ModelPage

from stroyprombeton.models import Category, Product
from stroyprombeton.tests.tests_forms import PriceFormTest, DrawingFormTest

CATEGORY_ROOT_NAME = 'Category root #0'


class CategoryTree(TestCase):

    fixtures = ['dump.json']

    def setUp(self):
        catalog_page = CustomPage.objects.get(slug='gbi')
        self.response = self.client.get(catalog_page.url)

    def test_root_category_response(self):
        status_code = self.response.status_code
        self.assertEqual(status_code, 200)

    def test_catalog_links(self):
        quantity = len(self.response.context['categories'])
        self.assertTrue(quantity > 0)


class CategoryTile(TestCase):
    """
    Test for CategoryPage view under the condition, that using CategoryTile
    template.
    """
    fixtures = ['dump.json']

    def setUp(self):
        """Create root and child category."""
        # TODO - move it in test_db. http://bit.ly/tail_2_test_db
        self.root_data = {
            'name': 'Test root category',
            'page': ModelPage.objects.create(
                content='Козырьки устанавливают над входами зданий.',
                name='Козырьки',
            ),
        }

        self.root_category = Category.objects.create(**self.root_data)

        self.child_data = {
            'name': 'Test child category',
            'parent': self.root_category,
            'page': ModelPage.objects.create(
                content='Козырьки применяют при строительстве зданий.',
                name='Козырьки входов, плиты парапетные.',
            )
        }

        Category.objects.create(**self.child_data)

        self.response = self.client.get('/gbi/categories/{}/'.format(self.root_category.id))

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
    """
    Test for CategoryPage view under the condition, that using CategoryTable
    template.
    """
    fixtures = ['dump.json']

    def setUp(self):
        """Create category and product."""
        self.root_data = {
            'name': 'Test root category',
            'page': ModelPage.objects.create(
                name='Козырьки',
                content='Козырьки устанавливают над входами зданий.',
            )
        }

        root_category = Category.objects.create(**self.root_data)

        self.product_data = {
            'price': 1447.21,
            'code': 350,
            'name': 'Test product name',
            'date_price_updated': datetime.now(),
            'category': root_category,
            'page': ModelPage.objects.create(
                name='Козырьки',
                content='Козырьки устанавливают над входами зданий.',
            )
        }

        Product.objects.create(**self.product_data)

        self.response = self.client.get('/gbi/categories/{}/'.format(root_category.id))

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
        quantity = len(self.response.context['products_with_images'])

        self.assertEqual(quantity, 1)

    def test_product_name(self):
        name = self.response.context['products_with_images'][0][0].name

        self.assertEqual(name, self.product_data['name'])

    def test_product_price(self):
        price = float(self.response.context['products_with_images'][0][0].price)

        self.assertEqual(price, self.product_data['price'])

    def test_product_code(self):
        code = self.response.context['products_with_images'][0][0].code

        self.assertEqual(code, self.product_data['code'])


class Product_(TestCase):
    """Test for ProductPage view."""

    fixtures = ['dump.json']

    def setUp(self):
        """Create category and product."""
        root_data = {
            'name': 'Test root category',
            'page': ModelPage.objects.create(h1='Category')
        }

        root_category = Category.objects.create(**root_data)

        self.product_data = {
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
            'page': ModelPage.objects.create(
                content='Козырьки устанавливают над входами зданий.',
                name='Козырьки',
            )
        }

        product = Product.objects.create(**self.product_data)

        self.response = self.client.get('/gbi/products/{}/'.format(product.id))

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
            self.assertFormError(
                response,
                'form',
                required_field,
                ['Пожалуйста, заполните это поле.']
            )

    def test_submit_invalid_email(self):
        wrong_fields = {'email': 'non@a/em.il'}
        response = self.client.post(self.URL, wrong_fields)
        self.assertFormError(
            response,
            'form',
            'email',
            ['Пожалуйста, введите корректный адрес электроной почты.']
        )


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

    def setUp(self):
        CustomPage.objects.create(slug='order-drawing')
        super(OrderDrawing, self).setUp()


class IndexPage(TestCase):

    fixtures = ['dump.json']

    def setUp(self):
        self.response = self.client.get('/')
        self.content = self.response.content.decode('utf-8')

    def test_has_news(self):
        self.assertIn('news-item', self.content)

    def test_has_link_on_region(self):
        """Index page should contain correct link to region."""
        region = FlatPage.objects.get(slug='empire-center-state')
        response = self.client.get(region.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, region.url)


class Search(TestCase):

    fixtures = ['dump.json']
    RIGHT_TERM = 'category #'
    WRONG_TERM = 'bugaga wrong term'

    def get_search_url(self, term=''):
        term = term or self.RIGHT_TERM
        # Use QueryDict to safely encode get params to url
        get_params = QueryDict(mutable=True)
        get_params.update({'term': term})
        return '{url}?{get_params}'.format(
            url=reverse('custom_page', args=('search',)),
            get_params=get_params.urlencode()
        )

    def test_result_page_contains_query(self):
        """Search results page should contain it's search query."""
        url = self.get_search_url(term=self.WRONG_TERM)
        response = self.client.get(url)
        self.assertNotContains(response, self.WRONG_TERM)


@override_settings(WKHTMLTOPDF_CMD='wkhtmltopdf')
class ProductPrice(TestCase):

    fixtures = ['dump.json']

    def test_price_list(self):
        """Context for pdf generation should include Category and Products."""
        self.response = self.client.get('/gbi/categories/1/pdf/')

        self.assertTrue(self.response['Content-Type'] == 'application/pdf')
        self.assertTrue(self.response.context['category'].name == CATEGORY_ROOT_NAME)
        self.assertTrue(len(self.response.context['products']) > 100)
