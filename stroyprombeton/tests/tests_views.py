"""
Views tests.

Note: there should be tests, subclassed from TestCase.
They all should be using Django's TestClient.

All Selenium-tests should be located in tests_selenium.
"""
import json
import unittest
from copy import copy
from datetime import datetime
from itertools import chain
from operator import attrgetter

from bs4 import BeautifulSoup
from django.conf import settings
from django.http import HttpResponse, QueryDict
from django.test import override_settings, TestCase, tag
from django.urls import reverse
from django.utils.translation import ugettext as _

from catalog.helpers import reverse_catalog_url
from pages.models import CustomPage, FlatPage, ModelPage
from stroyprombeton import models
from stroyprombeton.tests.helpers import CategoryTestMixin, create_doubled_tag
from stroyprombeton.tests.tests_forms import PriceFormTest

CANONICAL_HTML_TAG = '<link rel="canonical" href="{path}">'
CATEGORY_ROOT_NAME = 'Category root #0'


def json_to_dict(response: HttpResponse) -> dict():
    return json.loads(response.content)


class BaseCatalogTestCase(TestCase):

    fixtures = ['dump.json']

    def setUp(self):
        self.root_category = models.Category.objects.filter(parent=None).first()
        self.category = models.Category.objects.root_nodes().select_related('page').first()
        self.tags = models.Tag.objects.order_by(*settings.TAGS_ORDER).all()

    def get_category_url(
        self,
        category: models.Category = None,
        tags: models.TagQuerySet = None,
        sorting: int = None,
        query_string: dict = None,
    ):
        category = category or self.category
        return reverse_catalog_url(
            'category', {'category_id': category.id}, tags, sorting, query_string,
        )

    def get_category_page(self, *args, **kwargs):
        return self.client.get(self.get_category_url(*args, **kwargs))

    def get_category_soup(self, *args, **kwargs) -> BeautifulSoup:
        category_page = self.get_category_page(*args, **kwargs)
        return BeautifulSoup(
            category_page.content.decode('utf-8'),
            'html.parser'
        )


# @todo #340:60m Move TestPageMixin to some PageData class.
#  And remove CategoryTable().response field.
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


@tag('fast')
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


@tag('fast')
class CategoryTile(TestCase, TestPageMixin):
    """
    Test for CategoryPage view.

    With condition, that using CategoryTile template.
    """

    def setUp(self):
        """Create root and child category."""
        # @todo #142:30m Move tests custom data to test_db.
        #  Use this command `stroyprombeton/management/commands/test_db.py`
        self.data = {
            'name': 'Test root category',
            'page': ModelPage.objects.create(
                content='Козырьки устанавливают над входами зданий.',
                name='Козырьки',
            ),
        }

        self.root_category = models.Category.objects.create(**self.data)

        self.child_data = {
            'name': 'Test child category',
            'parent': self.root_category,
            'page': ModelPage.objects.create(
                content='Козырьки применяют при строительстве зданий.',
                name='Козырьки входов, плиты парапетные.',
            )
        }

        models.Category.objects.create(**self.child_data)

        self.response = self.client.get(f'/gbi/categories/{self.root_category.id}/')

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


@tag('fast')
class CategoryTable(BaseCatalogTestCase, TestPageMixin):
    """
    Test for CategoryPage view.

    With condition, that using CategoryTable template.
    """

    fixtures = ['dump.json']

    def setUp(self):
        """Create category and product."""
        super().setUp()

        category_data = {
            'name': 'Test root category',
            'page': ModelPage.objects.create(
                name='Козырьки',
                content='Козырьки устанавливают над входами зданий.',
            )
        }
        self.category = models.Category.objects.create(**category_data)

        self.data = {
            'price': 1447.21,
            'code': 350,
            'name': 'Test product name',
            'date_price_updated': datetime.now(),
            'category': self.category,
            'page': ModelPage.objects.create(
                name='Козырьки',
                content='Козырьки устанавливают над входами зданий.',
            )
        }
        models.Product.objects.create(**self.data)

        self.response = self.client.get(self.get_category_url())

    @property
    def response_product(self):
        return self.response.context['products'][0]

    def test_products_quantity(self):
        self.assertEqual(len(self.response.context['products']), 1)

    def test_product_name(self):
        self.assertEqual(
            self.response_product.name,
            self.data['name']
        )

    def test_product_price(self):
        self.assertEqual(
            float(self.response_product.price),
            self.data['price']
        )

    def test_product_code(self):
        self.assertEqual(
            self.response_product.code,
            self.data['code']
        )

    def test_inactive_product_not_in_category(self):
        test_product = models.Product.objects.first()
        test_product.page.is_active = False
        test_product.save()

        response = self.client.get(reverse('category', args=(test_product.category_id,)))
        self.assertNotIn(test_product, response.context['products'])

    def test_load_more_context_data(self):
        """App should response with products data on load_more request."""
        db_products = (
            models.Product.objects.active()
            .filter_descendants(self.root_category)
            .order_by(*settings.PRODUCTS_ORDERING)
        )

        response = self.client.post(
            reverse('fetch_products'),
            data={
                'categoryId': self.root_category.id,
                'offset': 10,
                'limit': 10,
            }
        )
        response_products = response.context['products']

        self.assertEqual(10, len(response_products))
        # check bounds of returned products list
        self.assertFalse(db_products[5] in response_products)
        self.assertTrue(db_products[15] in response_products)
        self.assertFalse(db_products[25] in response_products)

    def test_products_are_from_category(self):
        # leaf category
        category = models.Category.objects.get(name='Category #0 of #6')
        response = self.client.get(self.get_category_url(category))
        self.assertTrue(
            all(p.category == category for p in response.context['products'])
        )

    def test_products_are_paginated(self):
        """Category page should contain limited products list."""
        category = models.Category.objects.first()
        response = self.client.get(self.get_category_url(category))
        self.assertEqual(len(response.context['products']), settings.PRODUCTS_ON_PAGE_PC)


@tag('fast')
class Product_(TestCase, TestPageMixin):
    """Test for ProductPage view."""

    fixtures = ['dump.json']

    def setUp(self):
        """Create category and product."""
        category_data = {
            'name': 'Test root category',
            'page': ModelPage.objects.create(h1='Category', content='Test category')
        }

        root_category = models.Category.objects.create(**category_data)

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

        product = models.Product.objects.create(**self.data)
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


@tag('fast')
class OrderPrice(AbstractFormViewTest, TestCase):
    URL = '/order-price/'
    SUCCESS_URL = '/price-success/'
    FORM_TEST = PriceFormTest
    FIELDS = copy(PriceFormTest.FIELDS)

    def setUp(self):
        CustomPage.objects.create(slug='order-price')
        super(OrderPrice, self).setUp()


@tag('fast')
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


@tag('fast')
class RobotsPage(TestCase):

    fixtures = ['dump.json']

    def setUp(self):
        self.response = self.client.get('/robots.txt')

    def test_robots_success(self):
        self.assertEqual(self.response.status_code, 200)


@tag('fast')
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
        product = models.Product.objects.first()
        url = self.get_search_url(term=str(product.id))
        response = self.client.get(url, follow=True)
        self.assertContains(response, product.name)


@tag('fast')
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

    def test_autocomplete_has_only_active(self):
        """Autocomplete items should contain only active products."""
        test_product = models.Product.objects.first()
        test_product.page.is_active = False
        test_product.page.save()

        url = f'{reverse("autocomplete")}?term={test_product.name}'
        response = self.client.get(url)
        results = json_to_dict(response)

        self.assertTrue(all(
            test_product.name not in result['name'] for result in results
        ))


@tag('fast')
class ProductPrice(TestCase):

    fixtures = ['dump.json']

    def test_price_list(self):
        """Context for pdf generation should include Category and Products."""
        self.response = self.client.get('/gbi/categories/1/pdf/')

        self.assertTrue(self.response['Content-Type'] == 'application/pdf')
        self.assertTrue(self.response.context['category'].name == CATEGORY_ROOT_NAME)
        self.assertTrue(len(self.response.context['products']) > 100)


@tag('fast')
class CatalogTags(BaseCatalogTestCase, CategoryTestMixin):

    fixtures = ['dump.json']

    def test_category_page_contains_all_tags(self):
        """Category contains all Product's tags."""
        response = self.client.get(self.get_category_path())

        tags = set(chain.from_iterable(map(
            lambda x: x.tags.all(), (
                models.Product.objects
                .filter_descendants(self.category)
                .prefetch_related('tags')
            )
        )))

        tag_names = list(map(attrgetter('name'), tags))

        for tag_name in tag_names:
            self.assertContains(response, tag_name)

    def test_has_canonical_meta_tag(self):
        """Test that CategoryPage should contain canonical meta tag."""
        response = self.client.get(self.get_category_path())
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            CANONICAL_HTML_TAG.format(path=response.request['PATH_INFO']),
        )

    def test_tags_page_has_no_canonical_meta_tag(self):
        """Test that CategoryTagsPage should not contain canonical meta tag."""
        # ignore CPDBear
        response = self.client.get(self.get_category_path(tags=self.tags))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response,
            CANONICAL_HTML_TAG.format(path=response.request['PATH_INFO']),
        )

    def test_paginated_tags_page_has_no_canonical_meta_tag(self):
        """
        Test CategoryTagsPage with canonical tags.

        CategoryTagsPage with pagination (and sorting) options
        should not contain canonical meta tag.
        """
        # ignore CPDBear
        response = self.client.get(self.get_category_path(tags=self.tags))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response,
            CANONICAL_HTML_TAG.format(path=response.request['PATH_INFO'])
        )

    def test_contains_product_with_certain_tags(self):
        """Category page contains Product's related by certain tags."""
        tags = self.tags
        response = self.client.get(self.get_category_path(tags=tags))
        self.assertTrue(
            all(
                tags[0] in p.tags.all() or tags[1] in p.tags.all()
                for p in response.context['products']
            )
        )

    def test_tag_titles_content_disjunction(self):
        """
        Test CategoryTagsPage with canonical tags.

        CategoryTagsPage with tags "Напряжение 6В" и "Напряжение 24В"
        should contain tag_titles var content: "6В или 24В".
        """
        tag_group = models.TagGroup.objects.first()
        tags = tag_group.tags.order_by(*settings.TAGS_ORDER).all()  # Ignore CPDBear
        response = self.client.get(self.get_category_path(tags=tags))
        self.assertEqual(response.status_code, 200)
        delimiter = settings.TAGS_TITLE_DELIMITER
        tag_titles = delimiter.join(t.name for t in tags)
        self.assertContains(response, tag_titles)

    def test_tag_titles_content_conjunction(self):
        """
        Test CategoryTagsPage with canonical tags.

        CategoryTagsPage with tags "Напряжение 6В" и "Cила тока 1А" should
        contain tag_titles var content: "6В и 1А".
        """
        tag_groups = models.TagGroup.objects.order_by('position', 'name').all()
        tag_ids = [g.tags.first().id for g in tag_groups]
        tags = models.Tag.objects.filter(id__in=tag_ids)
        response = self.client.get(self.get_category_path(tags=tags))
        self.assertEqual(response.status_code, 200)
        delimiter = settings.TAG_GROUPS_TITLE_DELIMITER
        tag_titles = delimiter.join(t.name for t in tags)
        self.assertContains(response, tag_titles)

    def test_tags_var_in_db_template(self):
        """
        Test CategoryTagsPage with canonical tags.

        "tags" db template at CategoryTagsPage
        should render tag names. For example "1 м, 20 кг".
        """
        tags = models.Tag.objects.order_by(*settings.TAGS_ORDER).all()
        response = self.client.get(self.get_category_path(tags=tags))
        self.assertEqual(response.status_code, 200)
        tag_names = ', '.join([t.name for t in tags])
        self.assertContains(response, tag_names)

    def test_doubled_tag(self):
        """Category tags page filtered by the same tag from different tag groups."""
        tag_ = create_doubled_tag()
        response = self.client.get(
            self.get_category_path(tags=models.Tag.objects.filter(id=tag_.id))
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, tag_.name)
        delimiter = settings.TAG_GROUPS_TITLE_DELIMITER
        self.assertNotContains(response, delimiter.join(2 * [tag_.name]))

    # @todo #315:60m Render tags on product page
    @unittest.expectedFailure
    def test_product_tag_linking(self):
        """Product should contain links on CategoryTagPage for it's every tag."""
        product = models.Product.objects.first()
        self.assertGreater(product.tags.count(), 0)

        property_links = [
            reverse('category', kwargs={
                'category_id': product.category.id,
                'tags': tag_.slug,
            }) for tag_ in product.tags.all()
        ]
        response = self.client.get(product.url)
        for link in property_links:
            self.assertContains(response, link)

    def test_non_existing_tags_404(self):
        """Product should contain links on CategoryTagPage for it's every tag."""
        product = models.Product.objects.first()
        self.assertGreater(product.tags.count(), 0)

        bad_tag_url = reverse('category', kwargs={
            'category_id': product.category.id,
            'tags': 'non-existent-tag',
        })
        response = self.client.get(bad_tag_url)
        self.assertEqual(response.status_code, 404)

    @staticmethod
    def set_too_many_tags(product: models.Product, from_index: int, to_index: int):
        group = models.TagGroup.objects.first()
        models.Tag.objects.filter(group=group).delete()

        for i in range(from_index, to_index):
            product.tags.add(
                models.Tag.objects.get_or_create(
                    group=group,
                    name=f'{i} м',
                    slug=f'{i}-m',
                )[0]
            )
        product.save()

    # set tags limit to value "10" to check if
    # tags from-to label contains max numeric, but not alphabetical value.
    # For example we should see "от 1 м до 11 м", but not "от 1 м до 9 м".
    @override_settings(TAGS_UI_LIMIT=10)
    def test_too_many_tags_collapse(self):
        """
        Page should not contain too many tags.

        If page contains more then `settings.TAGS_UI_LIMIT` tags,
        it should collapse them and show short label instead.
        """
        from_index, to_index = 1, settings.TAGS_UI_LIMIT + 2
        product = (
            models.Product.objects
            .prefetch_related('category')
            .get(name='Product #10 of Category #0 of #3')
        )

        self.set_too_many_tags(product, from_index, to_index)

        tags_text = (
            self.get_category_soup(category=product.category)
            .find(class_='tags-filter-inputs')
            .text
        )
        self.assertIn(f'от {from_index} м до {to_index - 1} м', tags_text)
        self.assertGreater(product.tags.count(), settings.TAGS_UI_LIMIT)

    def test_filter_products_by_tags(self):
        """Category page should not contain products, excluded by tags selection."""
        tag_slug = '2-m'
        tag_qs = models.Tag.objects.filter(slug=tag_slug)
        tag = tag_qs.first()
        response = self.get_category_page(category=self.root_category, tags=tag_qs)

        # find product: it has no tag and it's descendant of root_category
        disappeared_products = (
            models.Product.objects.active()
            .prefetch_related('tags')
            .filter_descendants(self.root_category)
            .exclude(tags=tag)
        )
        self.assertFalse(
            any(p.name in response.content.decode() for p in disappeared_products)
        )
