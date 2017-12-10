"""
Views tests.

Note: there should be tests, subclassed from TestCase.
They all should be using Django's TestClient.

All Selenium-tests should be located in tests_selenium.
"""
import json
from copy import copy
from datetime import datetime

from django.http import HttpResponse, QueryDict
from django.test import TestCase
from django.urls import reverse
from django.utils.translation import ugettext as _

from pages.models import CustomPage, FlatPage, ModelPage

from stroyprombeton.models import Category, Product
from stroyprombeton.tests.tests_forms import PriceFormTest

CATEGORY_ROOT_NAME = 'Category root #0'


def json_to_dict(response: HttpResponse) -> dict():
    return json.loads(response.content)


class TestPageMixin:

    @property
    def page(self):
        return self.response.context['page']

    def test_response_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_page(self):
        self.assertTrue(self.page)

    def test_h1(self):
        self.assertEqual(
            self.page.h1,
            self.data['page'].h1
        )

    def test_content(self):
        self.assertEqual(
            self.page.content,
            self.data['page'].content
        )


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


class CategoryTile(TestCase, TestPageMixin):
    """
    Test for CategoryPage view.

    With condition, that using CategoryTile template.
    """

    def setUp(self):
        """Create root and child category."""
        # TODO - move it in test_db. http://bit.ly/tail_2_test_db
        self.data = {
            'name': 'Test root category',
            'page': ModelPage.objects.create(
                content='Козырьки устанавливают над входами зданий.',
                name='Козырьки',
            ),
        }

        self.root_category = Category.objects.create(**self.data)

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

    def test_children_categories_quantity(self):
        self.assertEqual(
            len(self.response.context['children']),
            1
        )

    def test_children_category_name(self):
        self.assertEqual(
            self.response.context['children'][0].name,
            self.child_data['name']
        )


class CategoryTable(TestCase, TestPageMixin):
    """
    Test for CategoryPage view.

    With condition, that using CategoryTable template.
    """

    fixtures = ['dump.json']

    def setUp(self):
        """Create category and product."""
        category_data = {
            'name': 'Test root category',
            'page': ModelPage.objects.create(
                name='Козырьки',
                content='Козырьки устанавливают над входами зданий.',
            )
        }

        root_category = Category.objects.create(**category_data)

        self.data = {
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

        Product.objects.create(**self.data)

        self.response = self.client.get('/gbi/categories/{}/'.format(root_category.id))

    @property
    def products_with_images(self):
        return self.response.context['products_with_images'][0][0]

    def test_products_quantity(self):
        self.assertEqual(len(self.response.context['products_with_images']), 1)

    def test_product_name(self):
        self.assertEqual(
            self.products_with_images.name,
            self.data['name']
        )

    def test_product_price(self):
        self.assertEqual(
            float(self.products_with_images.price),
            self.data['price']
        )

    def test_product_code(self):
        self.assertEqual(
            self.products_with_images.code,
            self.data['code']
        )

    def test_inactive_product_not_in_category(self):
        test_product = Product.objects.first()
        test_product.page.is_active = False
        test_product.save()

        response = self.client.get(reverse('category', args=(test_product.category_id,)))
        self.assertNotIn(test_product, response.context['products_with_images'])


class Product_(TestCase, TestPageMixin):
    """Test for ProductPage view."""

    fixtures = ['dump.json']

    def setUp(self):
        """Create category and product."""
        category_data = {
            'name': 'Test root category',
            'page': ModelPage.objects.create(h1='Category', content='Test category')
        }

        root_category = Category.objects.create(**category_data)

        self.data = {
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

        product = Product.objects.create(**self.data)

        self.response = self.client.get('/gbi/products/{}/'.format(product.id))

    @property
    def product(self):
        return self.response.context['product']

    def test_product_name(self):
        self.assertEqual(self.product.name, self.data['name'])

    def test_product_price(self):
        self.assertEqual(float(self.product.price), self.data['price'])

    def test_product_code(self):
        self.assertEqual(self.product.code, self.data['code'])

    def test_product_mark(self):
        self.assertEqual(int(self.product.mark), self.data['mark'])

    def test_product_length(self):
        self.assertEqual(self.product.length, self.data['length'])

    def test_product_width(self):
        self.assertEqual(self.product.width, self.data['width'])

    def test_product_height(self):
        self.assertEqual(self.product.height, self.data['height'])

    def test_product_diameter_in(self):
        self.assertEqual(
            self.product.diameter_in,
            self.data['diameter_in']
        )

    def test_product_diameter_out(self):
        self.assertEqual(
            self.product.diameter_out,
            self.data['diameter_out']
        )

    def test_product_weight(self):
        self.assertEqual(self.product.weight, self.data['weight'])

    def test_product_volume(self):
        self.assertEqual(self.product.volume, self.data['volume'])

    def test_product_specification(self):
        self.assertEqual(
            self.product.specification,
            self.data['specification']
        )

    def test_inactive_product_unavailable(self):
        product_id = self.product.id

        ModelPage.objects.filter(stroyprombeton_product=product_id).update(is_active=False)
        response = self.client.get(reverse('product', args=(product_id,)))

        self.assertEqual(response.status_code, 404)
        ModelPage.objects.filter(stroyprombeton_product=product_id).update(is_active=True)


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

    def setUp(self):
        CustomPage.objects.create(slug='order-price')
        super(OrderPrice, self).setUp()


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

    def test_search_by_id(self):
        """Search view should return redirect on model page, if id was received as term."""
        product = Product.objects.first()
        url = self.get_search_url(term=str(product.id))
        response = self.client.get(url, follow=True)
        self.assertContains(response, product.page.display_h1)


class TestSearch(TestCase):
    """Test all search methods: search page and autocompletes."""

    fixtures = ['dump.json']
    TERM = 'Prod'
    WRONG_TERM = 'Bugaga'  # it's short for trigram search testing

    def test_search_has_results(self):
        """Search page should contain at least one result for right term."""
        term = self.TERM
        response = self.client.get(
            f'/search/?term={term}',
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _('Product'))
        # search page should contain not only results.
        # But markup, menu links and so on.
        self.assertContains(response, '<title>')
        self.assertContains(response, '<td class="table-td table-name">')

    def test_search_no_results(self):
        """Search page should not contain results for wrong term."""
        term = self.WRONG_TERM
        response = self.client.get(
            f'/search/?term={term}',
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, '<div class="search-result-item">')

    def test_autocomplete_has_results(self):
        """Autocomplete should contain at least one result for right term."""
        term = self.TERM
        response = self.client.get(
            reverse('autocomplete') + f'?term={term}'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(json_to_dict(response))
        self.assertContains(response, term)

    def test_autocomplete_no_results(self):
        """Autocomplete should not contain results for wrong term."""
        term = self.WRONG_TERM
        response = self.client.get(
            reverse('autocomplete') + f'?term={term}'
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(json_to_dict(response))
        self.assertNotContains(response, term)

    def test_admin_autocomplete_has_results(self):
        """Admin autocomplete should contain at least one result for right term."""
        term = self.TERM
        page_type = 'product'
        querystring = f'?term={term}&pageType={page_type}'
        response = self.client.get(reverse('admin_autocomplete') + querystring)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(json_to_dict(response))
        self.assertContains(response, term)

    def test_admin_autocomplete_no_results(self):
        """Admin autocomplete should contain no results for wrong term."""
        term = self.WRONG_TERM
        page_type = 'product'
        querystring = f'?term={term}&pageType={page_type}'
        response = self.client.get(reverse('admin_autocomplete') + querystring)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(json_to_dict(response))
        self.assertNotContains(response, term)


class ProductPrice(TestCase):

    fixtures = ['dump.json']

    def test_price_list(self):
        """Context for pdf generation should include Category and Products."""
        self.response = self.client.get('/gbi/categories/1/pdf/')

        self.assertTrue(self.response['Content-Type'] == 'application/pdf')
        self.assertTrue(self.response.context['category'].name == CATEGORY_ROOT_NAME)
        self.assertTrue(len(self.response.context['products']) > 100)
