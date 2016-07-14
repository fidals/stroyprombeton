"""
Views tests.

Note: there should be tests, subclassed from TestCase.
They all should be using Django's TestClient.

All Selenium-tests should be located in tests_selenium.
"""
from datetime import datetime

from django.test import TestCase

from stroyprombeton.models import Category, Product


class CategoryTree(TestCase):
    """Tests for CategoryTree view """

    @classmethod
    def setUpTestData(cls):
        """Create root and child category."""
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
        cls.root_data = {
            'h1': 'Козырьки',
            'content': 'Козырьки устанавливают над входами зданий.',
            'name': 'Test root category'
        }

        cls.child_data = {
            'h1': 'Козырьки входов, плиты парапетные.',
            'content': 'Козырьки применяют при строительстве зданий.',
            'name': 'Test child category'
        }

        root_category = Category.objects.create(id=1, **cls.root_data)

        Category.objects.create(
            id=2,
            parent=root_category,
            **cls.child_data
        )

    def setUp(self):
        """Get response from /gbi/categories/1/"""
        self.response = self.client.get('/gbi/categories/1/')

    def test_response_status_code(self):
        status_code = self.response.status_code

        self.assertEqual(status_code, 200)

    def test_breadcrumbs(self):
        breadcrumbs = self.response.context['breadcrumbs']

        self.assertEqual(len(breadcrumbs), 3)

    def test_h1(self):
        h1 = self.response.context['category'].h1

        self.assertEqual(h1, self.root_data['h1'])

    def test_content(self):
        content = self.response.context['category'].content

        self.assertEqual(content, self.root_data['content'])

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
        cls.root_data = {
            'h1': 'Козырьки',
            'name': 'Test root category',
            'content': 'Козырьки устанавливают над входами зданий.',
        }

        cls.product_data = {
            'price': 1447.21,
            'code': 350,
            'name': 'Test product name',
            'date_price_updated': datetime.now()
        }

        root_category = Category.objects.create(id=1, **cls.root_data)

        Product.objects.create(category=root_category, **cls.product_data)

    def setUp(self):
        """Get response from /gbi/categories/1/"""
        self.response = self.client.get('/gbi/categories/1/')

    def test_response_status_code(self):
        status_code = self.response.status_code

        self.assertEqual(status_code, 200)

    def test_breadcrumbs(self):
        breadcrumbs = self.response.context['breadcrumbs']

        self.assertEqual(len(breadcrumbs), 3)

    def test_h1(self):
        h1 = self.response.context['category'].h1

        self.assertEqual(h1, self.root_data['h1'])

    def test_content(self):
        content = self.response.context['category'].content

        self.assertEqual(content, self.root_data['content'])

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

        root_data = {
            'h1': 'Козырьки',
            'name': 'Test root category',
            'content': 'Козырьки устанавливают над входами зданий.',
        }

        cls.product_data = {
            'name': 'Test product name',
            'h1': 'Плита парапетная железобетонная АП 13.5',
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
            'date_price_updated': datetime.now()
        }

        root_category = Category.objects.create(
            id=1,
            **root_data
        )

        Product.objects.create(
            id=1,
            category=root_category,
            **cls.product_data
        )

    def setUp(self):
        self.response = self.client.get('/gbi/products/1/')

    def test_response_status_code(self):
        status_code = self.response.status_code

        self.assertEqual(status_code, 200)

    def test_status_breadcrumbs(self):
        breadcrumbs = self.response.context['breadcrumbs']

        self.assertEqual(len(breadcrumbs), 4)

    def test_h1(self):
        h1 = self.response.context['product'].h1

        self.assertEqual(h1, self.product_data['h1'])

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
