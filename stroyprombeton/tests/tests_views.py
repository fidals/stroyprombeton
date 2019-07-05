"""
Views tests.

Note: there should be tests, subclassed from TestCase.
They all should be using Django's TestClient.

All Selenium-tests should be located in tests_selenium.
"""
import json
import unittest
from copy import copy
from itertools import chain
from operator import attrgetter

from bs4 import BeautifulSoup
from django.conf import settings
from django.db.models import Count
from django.http import HttpResponse, QueryDict
from django.test import override_settings, TestCase, tag
from django.urls import reverse
from django.utils.translation import ugettext as _

from catalog.helpers import reverse_catalog_url
from pages.models import CustomPage, FlatPage, ModelPage
from stroyprombeton import context, models, request_data
from stroyprombeton.tests.helpers import CategoryTestMixin
from stroyprombeton.tests.tests_forms import PriceFormTest

CANONICAL_HTML_TAG = '<link rel="canonical" href="{base_url}{path}">'
CATEGORY_ROOT_NAME = 'Category root #0'
PRODUCT_WITH_IMAGE = 110
OPTION_WITH_IMAGE = 220


def json_to_dict(response: HttpResponse) -> dict():
    return json.loads(response.content)


class BaseCatalogTestCase(TestCase):

    fixtures = ['dump.json']

    def setUp(self):
        self.root_category = models.Category.objects.filter(parent=None).first()
        self.category = models.Category.objects.root_nodes().select_related('page').first()
        self.tags = models.Tag.objects.order_by_alphanumeric().all()

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

    def get_page_number(self, response):
        return response.context['paginated']['page'].number


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


@tag('fast', 'catalog')
class Category(BaseCatalogTestCase, TestPageMixin):
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
            'name': 'Test product name',
            'category': self.category,
            'page': ModelPage.objects.create(
                name='Козырьки',
                content='Козырьки устанавливают над входами зданий.',
            )
        }
        # @todo #419:30m  Rm models creation in favour of fixtures.
        #  At the tests.
        product = models.Product.objects.create(**self.data)
        models.Option.objects.create(
            price=100,
            mark=f'Some mark',
            product=product,
        )

        self.response = self.client.get(self.get_category_url())

    def test_inactive_product_not_in_category(self):
        test_product = models.Product.objects.first()
        test_product.page.is_active = False
        test_product.save()

        response = self.client.get(reverse('category', args=(test_product.category_id,)))
        self.assertNotIn(test_product, response.context['products'])

    # @todo #514:30m  Regroup `test_fetch_products_*` tests.
    #  Create a separated class for them.
    def test_fetch_products_context_data(self):
        """App should response with products data on fetch_products request."""
        db_options = (
            models.Option.objects.active()
            .filter_descendants(self.root_category)
            .order_by(*settings.OPTIONS_ORDERING)
        )

        response = self.client.post(
            reverse('fetch_products'),
            data={
                'categoryId': self.root_category.id,
                'offset': 10,
                'limit': 10,
            }
        )
        self.assertEqual(200, response.status_code)
        response_products = response.context['products']
        self.assertIsInstance(response_products[0], models.Option)

        self.assertEqual(10, len(response_products))
        # check bounds of returned products list
        self.assertTrue(db_options[5] not in response_products)
        self.assertTrue(db_options[15] in response_products)
        self.assertTrue(db_options[25] not in response_products)

    def test_fetch_products_bad_request_processing(self):
        response = self.client.post(reverse('fetch_products'), data={})
        self.assertEqual(400, response.status_code)

    def test_fetch_positions_searching(self):
        term = '#1'
        category = models.Category.objects.get(name='Category #0 of #1')
        options = models.Option.objects.filter_descendants(category)
        searched = context.options.search(  # Ignore CPDBear
            term, options, context.options.Searched.LOOKUPS,
            ordering=('product__name', )
        )

        response = self.client.post(
            reverse('fetch_products'),
            data={
                'categoryId': category.id,  # Ignore CPDBear
                'filtered': 'true',
                'term': term,
                'offset': 0,
                'limit': 10**6,
            }
        )
        self.assertEqual(searched.count(), len(response.context['products']))
        self.assertEqual(list(searched), list(response.context['products']))

    def test_products_are_from_category(self):
        # leaf category
        category = models.Category.objects.get(name='Category #0 of #44')
        response = self.client.get(self.get_category_url(category))
        self.assertTrue(
            all(option.product.category == category for option in response.context['products'])
        )

    def test_products_are_paginated(self):
        """Category page should contain limited products list."""
        category = models.Category.objects.first()
        response = self.client.get(self.get_category_url(category))
        self.assertEqual(
            len(response.context['products']),
            request_data.Category.PRODUCTS_ON_PAGE_PC
        )

    def test_total_products(self):
        category = models.Category.objects.first()
        options = models.Option.objects.filter_descendants(category)
        response = self.client.get(self.get_category_url(category))
        self.assertEqual(
            options.count(),
            int(response.context['paginated']['total_products'])
        )
        self.assertContains(response, options.count())

    def test_total_products_filtered(self):
        """Fast analog of `test_tag_button_filter_products` slow test."""
        # this category contains 25 tags. It's less then products on page limit.
        category = models.Category.objects.get(name='Category #1 of #2')
        tags = models.Tag.objects.filter(slug='1-m')
        options = (
            models.Option.objects
            .bind_fields()
            .filter_descendants(category)
            .tagged_or_all(tags)
        )
        soup = self.get_category_soup(category, tags=tags)
        total = int(soup.find(id='load-more-products')['data-total-products'])
        self.assertEqual(total, options.count())

    def test_active_options(self):
        """Category page should contain only options with active related products."""
        options_qs = (
            models.Option.objects
            .bind_fields()
            .filter_descendants(self.root_category)  # Ignore CPDBear
            .order_by(*settings.OPTIONS_ORDERING)
        )
        # make inactive the first option in a category page list
        inactive = options_qs.first()
        inactive.product.page.is_active = False
        inactive.product.page.save()
        active = options_qs.active().first()

        response = self.client.get(self.get_category_url(self.root_category))
        self.assertIn(active, response.context['products'])
        self.assertNotIn(inactive, response.context['products'])

    def test_product_images(self):
        # product with image
        # @todo #665:30m  In tests get product-option with image from DB.
        #  Reuse the getting all over the tests.
        product = models.Product.objects.get(id=PRODUCT_WITH_IMAGE)
        response = self.client.get(product.category.url)  # Ignore CPDBear
        image = response.context['product_images'][OPTION_WITH_IMAGE]
        self.assertTrue(image)
        self.assertTrue(image.image.url)

    def test_product_image_button(self):
        """Category page should contain button to open existing product image."""
        # product with image
        product = models.Product.objects.get(id=PRODUCT_WITH_IMAGE)  # Ignore CPDBear
        response = self.client.get(product.category.url)
        self.assertContains(response, 'table-photo-ico')

    def test_category_matrix_page(self):
        """Matrix page should contain all second level categories."""
        page = CustomPage.objects.get(slug='gbi')
        response = self.client.get(page.url)
        soup = BeautifulSoup(
            response.content.decode('utf-8'),
            'html.parser'
        )
        self.assertEqual(200, response.status_code)

        second_level_db = (
            models.Category.objects
            .active()
            .filter(parent__in=models.Category.objects.filter(parent=None))
            .order_by('page__position', 'parent__name', 'name')
        )
        second_level_app = soup.find_all(class_='second-level-category')
        for from_db, from_app in zip(second_level_db, second_level_app):
            self.assertEqual(from_db.name, from_app.a.text)

    # @todo #721:30m  Fix category links on series.
    #  Launch the test below to get details.
    @unittest.expectedFailure
    def test_links_on_series(self):
        """Category should contain it's series list with links."""
        option = models.Option.objects.filter(series__isnull=False).first()
        category = option.product.category
        soup = self.get_category_soup(category)
        series_app = soup.find_all(class_='series-filter-link')
        response = self.client.get(series_app[0]['href'])
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            [s.name for s in category.get_series()],
            [s.text.strip() for s in series_app]
        )

    def test_links_on_sections(self):
        """Category should contain it's sections list with links."""
        product = models.Product.objects.filter(section__isnull=False).first()
        category = product.category
        soup = self.get_category_soup(category)
        sections_app = soup.find_all(class_='section-filter-link')
        response = self.client.get(sections_app[0]['href'])
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            [s.name for s in category.get_sections()],
            [s.text.strip() for s in sections_app]
        )

    def test_empty_products_404(self):
        """Category with no products should return 404 response."""
        category = models.Category.objects.get(name='Category root empty #17')
        response = self.get_category_page(category)
        self.assertEqual(404, response.status_code)


@tag('fast', 'catalog')
class CatalogPagination(BaseCatalogTestCase):

    def assert_pagination_link(self, link, page_number):
        """Page numbers from link href and from link anchor should be equal."""
        self.assertEqual(
            self.get_page_number(self.client.get(link['href'])),
            page_number,
        )

    def get_category_soup(self, page_number: int) -> BeautifulSoup:
        return super().get_category_soup(query_string={'page': page_number})

    def test_pagination_numbering(self):
        page_number = 1
        response = self.get_category_page(query_string={'page': page_number})
        self.assertEqual(self.get_page_number(response), page_number)

    def test_nearest_links(self):
        """A page in the middle of pagination has previous and next pages."""
        page_number = 2
        response = self.get_category_page(query_string={'page': page_number})

        self.assertTrue(response.context['paginated']['page'].has_previous())
        self.assertTrue(response.context['paginated']['page'].has_next())

    def test_nearest_numbers(self):
        page_number = 2
        response = self.get_category_page(query_string={'page': page_number})

        self.assertEqual(
            response.context['paginated']['page'].previous_page_number(),
            page_number - 1,
        )
        self.assertEqual(
            response.context['paginated']['page'].next_page_number(),
            page_number + 1,
        )

    def test_pagination_step(self):
        """Category page contains `pagination_step` count of products in list."""
        pagination_step = 25
        response = self.get_category_page(query_string={'step': pagination_step})
        self.assertEqual(len(response.context['paginated']['page'].object_list), pagination_step)

    def test_pagination_404(self):
        """Category page returns 404 for a nonexistent page number."""
        self.assertEqual(
            self.get_category_page(query_string={'page': 1000}).status_code,
            404,
        )

    def test_numbered_pagination_links(self):
        """Forward to numbered pagination pages."""
        page_number = 3
        _, *numbered, _ = self.get_category_soup(page_number).find(
            class_='js-seo-links').find_all('a')

        for slice, link in zip([-2, -1, 1, 2], numbered):
            self.assert_pagination_link(link, page_number + slice)

    def test_arrow_pagination_links(self):
        """Each button forward to a previous and a next pagination pages."""
        page_number = 2
        prev, *_, next_ = self.get_category_soup(page_number).find(
            class_='js-seo-links').find_all('a')

        self.assert_pagination_link(next_, page_number + 1)
        self.assert_pagination_link(prev, page_number - 1)

    def test_pagination_canonical(self):
        """Canonical links forward to a previous and a next pagination pages."""
        page_number = 2
        soup = self.get_category_soup(page_number)

        self.assert_pagination_link(
            soup.find('link', attrs={'rel': 'next'}),
            page_number + 1
        )
        self.assert_pagination_link(
            soup.find('link', attrs={'rel': 'prev'}),
            page_number - 1
        )


# @todo  #465:30m  Improve tests_views.Product
#  Use only fixtures, create shared response helper
#  like `shopelectro.tests.tests_views.BaseCatalogTestCase#get_category_page` does.
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
            'page': ModelPage.objects.create(
                content='Козырьки устанавливают над входами зданий.',
                name='Козырьки',
            )
        }

        product = models.Product.objects.create(**self.data)
        self.response = self.client.get(f'/gbi/products/{product.id}/')

    def get_product_soup(self, product: models.Product) -> BeautifulSoup:
        page = self.client.get(product.url)
        return BeautifulSoup(
            page.content.decode('utf-8'),
            'html.parser'
        )

    @property
    def product(self):
        return self.response.context['product']

    def test_inactive_product_unavailable(self):
        product_id = self.product.id

        ModelPage.objects.filter(stroyprombeton_product=product_id).update(is_active=False)
        response = self.client.get(reverse('product', args=(product_id,)))

        self.assertEqual(response.status_code, 404)
        ModelPage.objects.filter(stroyprombeton_product=product_id).update(is_active=True)

    def test_tags_table(self):
        """Options table should contain right tags set."""
        option = models.Option.objects.filter(tags__isnull=False).first()
        response = self.client.get(option.product.url)
        tags = list(option.tags.all().order_by_alphanumeric())
        table = BeautifulSoup(
            response.content.decode('utf-8'),
            'html.parser'
        ).find(class_='options-table')
        # the first column is hardcoded field mark
        groups = table.find_all('th')[1:]
        for tag_, group in zip(tags, groups):
            self.assertIn(tag_.group.name, group)

        parsed_tags = table.find_all('tr')[1].find_all(class_='option-td')[1:]
        for tag_, parsed in zip(tags, parsed_tags):
            self.assertEqual(tag_.name, parsed.string.strip())

    def test_series_label(self):
        series = models.Series.objects.first()
        product = series.options.first().product
        soup = self.get_product_soup(product)
        link = soup.find(class_='product-serial-val')

        self.assertEqual(series.name, link.text.strip())
        self.assertEqual(series.url, link['href'])


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


# @todo #60m:  Create arch for the Search tests.
#  Create code, that will be able to test search
#  by dataset presented in pattern "term -> results".
#  Maybe hypothesis lib will be helpful for it.
@tag('fast')
class Search(TestCase):
    """Test all search methods: search page and autocompletes."""

    fixtures = ['dump.json']
    TERM = 'Prod'
    WRONG_TERM = 'Bugaga'  # it's short for trigram search testing

    def get_search_url(self, term=''):
        term = term or self.RIGHT_TERM
        # Use QueryDict to safely encode get params to url
        get_params = QueryDict(mutable=True)
        get_params.update({'term': term})
        return '{url}?{get_params}'.format(
            url=reverse('custom_page', args=('search',)),
            get_params=get_params.urlencode()
        )

    def search(self, term=''):
        return self.client.get(self.get_search_url(term), follow=True)

    def get_results_soup(self, *args, **kwargs):
        return BeautifulSoup(
            self.search(*args, **kwargs).content.decode('utf-8'),
            'html.parser'
        )

    # @todo #626:30m Bring back a search query to search results page's input.
    @unittest.expectedFailure
    def test_search_query_on_result_page(self):
        """The search query appears in search input of search results page."""
        self.assertContains(
            self.search(term=self.WRONG_TERM),
            self.WRONG_TERM,
        )

    # @todo #622:60m  Fix search engine logic.
    #  If query fully equals some product.name,
    #  search results should return this product as the first results entry.
    @unittest.expectedFailure
    def test_search_by_product_name(self):
        """Search results page should contain product names."""
        product = models.Product.objects.first()
        soup = self.get_results_soup(term=product.name)
        first = soup.find(class_='table-link')
        self.assertEqual(product.name, first.text.strip())

    def test_id_results(self):
        """Search view should return redirect on model page, if id was received as term."""
        product = models.Product.objects.first()
        self.assertContains(
            self.search(term=str(product.id)),
            product.name,
        )

    def test_some_results(self):
        """Search page should contain at least one result for right term."""
        response = self.search(term=self.TERM)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _('Product'))
        # search page should contain not only results.
        # But markup, menu links and so on.
        self.assertContains(response, '<title>')
        self.assertContains(response, '<td class="table-td table-name">')

    def test_series_results(self):
        """Search page should contain at least one result for right term."""
        response = self.search(term='Serie')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _('Series'))
        # search page should contain not only results.
        # But markup, menu links and so on.
        self.assertContains(response, '<title>')
        self.assertContains(response, '<td class="table-td table-name">')

    def test_no_results(self):
        """Search page should not contain results for wrong term."""
        response = self.search(term=self.WRONG_TERM)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, '<div class="search-result-item">')


@tag('fast')
class Autocomplete(TestCase):

    fixtures = ['dump.json']
    TERM = 'Prod'
    WRONG_TERM = 'Bugaga'  # it's short for trigram search testing

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


@tag('fast', 'catalog')
class CatalogTags(BaseCatalogTestCase, CategoryTestMixin):

    fixtures = ['dump.json']

    def test_category_page_contains_all_tags(self):
        """Category contains all Product's tags."""
        response = self.client.get(self.get_category_path())

        products = models.Product.objects.filter_descendants(self.category)
        tags = set(chain.from_iterable(map(
            lambda x: x.tags.all(), (
                models.Option.objects
                .filter(product__in=products)
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
            CANONICAL_HTML_TAG.format(
                base_url=settings.BASE_URL,
                path=response.request['PATH_INFO']
            )
        )

    def test_tags_page_has_no_canonical_meta_tag(self):
        """Test that CategoryTagsPage should not contain canonical meta tag."""
        # ignore CPDBear
        response = self.client.get(self.get_category_path(tags=self.tags))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response,
            CANONICAL_HTML_TAG.format(
                base_url=settings.BASE_URL,
                path=response.request['PATH_INFO']
            )
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
            CANONICAL_HTML_TAG.format(
                base_url=settings.BASE_URL,
                path=response.request['PATH_INFO']
            )
        )

    def test_contains_product_with_certain_tags(self):
        """Category page contains Product's related by certain tags."""
        category = models.Category.objects.get(name='Category #0 of #41')
        options = [p.options.first() for p in category.products.all()]
        tags = (
            models.Tag.objects
            .filter(options__in=options)
            .order_by_alphanumeric()
            .distinct()
        )
        response = self.client.get(self.get_category_path(category=category, tags=tags))
        self.assertTrue(
            all(
                tags[0] in option.tags.all() or tags[1] in option.tags.all()
                for option in response.context['products']
            )
        )

    def test_tag_titles_content_disjunction(self):
        """
        Test CategoryTagsPage with canonical tags.

        CategoryTagsPage with tags "Напряжение 6В" и "Напряжение 24В"
        should contain tag_titles var content: "6В или 24В".
        """
        tag_group = models.TagGroup.objects.first()
        tags = tag_group.tags.order_by_alphanumeric().all()  # Ignore CPDBear
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
        tags = models.Tag.objects.order_by_alphanumeric().all()
        response = self.client.get(self.get_category_path(tags=tags))
        self.assertEqual(response.status_code, 200)
        tag_names = ', '.join([t.name for t in tags])
        self.assertContains(response, tag_names)

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
        """Existing category with a non existing tag should return 404."""
        product = models.Product.objects.first()
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
        option = product.options.first()

        for i in range(from_index, to_index):
            option.tags.add(
                models.Tag.objects.get_or_create(
                    group=group,
                    name=f'{i} м',
                    slug=f'{i}-m',
                )[0]
            )
        option.save()

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
            .get(name='Product #10 of Category #0 of #41')
        )

        self.set_too_many_tags(product, from_index, to_index)

        tags_text = (
            self.get_category_soup(category=product.category)
            .find(class_='tags-filter-inputs')
            .text
        )
        self.assertIn(f'от {from_index} м до {to_index - 1} м', tags_text)
        self.assertGreater(product.options.first().tags.count(), settings.TAGS_UI_LIMIT)

    def test_filter_options_by_tags(self):
        """Category page should not contain options, excluded by tags selection."""
        tag = models.Tag.objects.filter_by_options(
            options=models.Option.objects.filter_descendants(self.root_category)
        ).first()
        tag_qs = models.Tag.objects.filter(slug=tag.slug)
        soup = self.get_category_soup(category=self.root_category, tags=tag_qs[1:])
        options = soup.find(class_='product-list').find_all(class_='table-link')
        returned = {o.text for o in options}

        disappeared_qs = (
            models.Option.objects
            .bind_fields().active()
            .filter_descendants(self.root_category)
            .exclude(tags=tag)
        )
        disappeared = {d.catalog_name for d in disappeared_qs}
        self.assertFalse(returned.intersection(disappeared))


# don't create SectionMatrix test to avoid tests code doubling.
# At #631 we'll get rid of the doubling.
@tag('fast', 'catalog')
class SeriesMatrix(BaseCatalogTestCase):
    fixtures = ['dump.json']

    def get_page_url(self):
        page = CustomPage.objects.get(slug='series')
        return page.url

    def get_page(self):
        return self.client.get(self.get_page_url())  # Ignore CPDBear

    def get_page_soup(self) -> BeautifulSoup:
        page = self.get_page()
        return BeautifulSoup(
            page.content.decode('utf-8'),
            'html.parser'
        )

    def test_page(self):
        self.assertEqual(200, self.get_page().status_code)

    def test_series_are_active(self):
        """Every series presented in series list should be active."""
        response = self.get_page()
        db_series = (
            models.Series.objects.bind_fields()
            .exclude_empty()
            .order_by('name')
        )
        app_series = list(chain.from_iterable(
            response.context['parted_items']
        ))
        self.assertEqual(db_series.count(), len(app_series))
        self.assertTrue(
            all(
                from_db == from_app
                for from_db, from_app in zip(db_series, app_series)
            )
        )


@tag('fast', 'catalog')
class Series(BaseCatalogTestCase):
    fixtures = ['dump.json']

    def setUp(self):
        self.series = models.Series.objects.filter(options__isnull=False).first()

    def get_series_url(
        self,
        series: models.Series = None,
    ):
        series = series or self.series
        return reverse('series', kwargs={'series_slug': series.slug})

    def get_series_page(self, *args, **kwargs):
        return self.client.get(self.get_series_url(*args, **kwargs))  # Ignore CPDBear

    def get_series_soup(self, *args, **kwargs) -> BeautifulSoup:
        series_page = self.get_series_page(*args, **kwargs)
        return BeautifulSoup(
            series_page.content.decode('utf-8'),
            'html.parser'
        )

    def test_options_are_from_series(self):
        response = self.client.get(self.get_series_url(self.series))
        self.assertTrue(
            all(option.series == self.series for option in response.context['products'])
        )

    def test_active_options(self):
        """Series page should contain only options with active related products."""
        options_qs = (
            self.series.options  # Ignore CPDBear
            .bind_fields()
            .order_by(*settings.OPTIONS_ORDERING)
        )
        # make inactive the first option in a series page list
        inactive = options_qs.first()
        inactive.product.page.is_active = False
        inactive.product.page.save()
        active = options_qs.active().first()

        response = self.client.get(self.get_series_url(self.series))
        self.assertIn(active, response.context['products'])
        self.assertNotIn(inactive, response.context['products'])

    def test_emtpy_404(self):
        """Series with not active options should return response 404."""
        series = (
            models.Series.objects
            .annotate(count=Count('options'))
            .filter(count=0)
        ).first()
        response = self.get_series_page(series)
        self.assertEqual(404, response.status_code)

    def test_product_images(self):
        """Series page should contain only options with active related products."""
        # product with image
        product = models.Product.objects.get(id=PRODUCT_WITH_IMAGE)
        series = models.Series.objects.first()
        product.options.update(series=series)
        response = self.client.get(series.url)  # Ignore CPDBear
        image = response.context['product_images'][110]
        self.assertTrue(image)
        self.assertTrue(image.image.url)

    def test_product_image_button(self):
        """Series page should contain button to open existing product image."""
        # product with image
        product = models.Product.objects.get(id=PRODUCT_WITH_IMAGE)  # Ignore CPDBear
        response = self.client.get(product.category.url)
        self.assertContains(response, 'table-photo-ico')


@tag('fast', 'catalog')
class Section(BaseCatalogTestCase):
    fixtures = ['dump.json']

    def setUp(self):
        self.section = models.Section.objects.filter(products__isnull=False).first()

    def get_section_url(
        self,
        section: models.Section = None,
    ):
        section = section or self.section
        return section.url

    def get_section_page(self, *args, **kwargs):
        return self.client.get(self.get_section_url(*args, **kwargs))  # Ignore CPDBear

    def get_section_soup(self, *args, **kwargs) -> BeautifulSoup:
        section_page = self.get_section_page(*args, **kwargs)
        return BeautifulSoup(
            section_page.content.decode('utf-8'),
            'html.parser'
        )

    def test_page_success(self):
        section = models.Section.objects.first()
        response = self.client.get(section.url)
        self.assertEqual(200, response.status_code)

    def test_products_are_from_section(self):
        response = self.client.get(self.get_section_url(self.section))
        self.assertTrue(
            all(p.section == self.section for p in response.context['products']),
            response.context['products']
        )

    def test_active_options(self):
        """Section page should contain only options with active related products."""
        products = self.section.products.bind_fields()
        # make inactive the first option in a section page list
        inactive = products.first()
        inactive.page.is_active = False
        inactive.page.save()
        active = products.active().first()

        response = self.client.get(self.get_section_url(self.section))
        self.assertIn(active, response.context['products'])
        self.assertNotIn(inactive, response.context['products'])

    def test_emtpy_404(self):
        """Section with not active options should return response 404."""
        section = (
            models.Section.objects
            .annotate(count=Count('products'))
            .filter(count=0)
        ).first()
        response = self.get_section_page(section)
        self.assertEqual(404, response.status_code)

    def test_product_images(self):
        """Section page should contain only options with active related products."""
        # product with image
        product = models.Product.objects.get(id=PRODUCT_WITH_IMAGE)
        product.section = models.Section.objects.first()
        product.save()
        response = self.client.get(product.section.url)
        image = response.context['product_images'][110]
        self.assertTrue(image)
        self.assertTrue(image.image.url)

    def test_product_image_button(self):
        """Section page should contain button to open existing product image."""
        # product with image
        product = models.Product.objects.get(id=PRODUCT_WITH_IMAGE)
        response = self.client.get(product.category.url)
        self.assertContains(response, 'table-photo-ico')


@tag('fast', 'catalog')
class SeriesByCategory(BaseCatalogTestCase):
    fixtures = ['dump.json']

    @staticmethod
    def get_series_url(series: models.Series, category: models.Category):
        return reverse(
            'series_by_category', kwargs={
                'series_slug': series.slug,
                'category_id': category.id
            }
        )

    def get_series_page(self, *args, **kwargs):
        return self.client.get(self.get_series_url(*args, **kwargs))

    def get_series_soup(self, *args, **kwargs) -> BeautifulSoup:
        series_page = self.get_series_page(*args, **kwargs)
        return BeautifulSoup(
            series_page.content.decode('utf-8'),
            'html.parser'
        )

    def test_filter_by_category(self):
        """
        Series+category page should contain only "right" options.

        Right options belongs to the series and to the category together.
        """
        series = models.Series.objects.first()
        product = series.options.first().product
        category_to_exclude = product.category
        category_to_include = (
            models.Category.objects
            .exclude(id=category_to_exclude.id)
            .annotate(count=Count('products'))
            .filter(count__gt=0)
            .first()
        )
        option_to_include = category_to_include.products.first().options.first()
        option_to_include.series = series
        option_to_include.save()
        self.assertEqual(1, series.options.filter(product__category=category_to_include).count())

        soup = self.get_series_soup(series, category_to_include)
        options_app = soup.find_all(class_='table-link')
        self.assertEqual(1, len(options_app))
        self.assertEqual(
            option_to_include.catalog_name,
            options_app[0].text.strip()
        )
