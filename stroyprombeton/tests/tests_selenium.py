import unittest
from urllib.parse import urljoin

from django.conf import settings
from django.core import mail
from django.template.defaultfilters import floatformat
from django.test import tag
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC, ui

from pages.urls import reverse_custom_page
from stroyprombeton import models as stb_models, request_data
from stroyprombeton.tests import helpers as test_helpers


def hover(browser, element):
    """Perform a hover over an element."""
    hover_action = ActionChains(browser).move_to_element(element)
    hover_action.perform()


def header_product_count(self):
    element = self.wait.until(EC.visibility_of_element_located(
        (By.CLASS_NAME, 'js-header-product-count')
    ))
    return element.text


def wait_page_loading(browser):
    ui.WebDriverWait(browser, 60).until(
        EC.visibility_of_element_located(
            (By.CLASS_NAME, 'content')
        )
    )


class SeleniumTestCase(test_helpers.BaseSeleniumTestCase):
    """Common superclass for running selenium-based tests."""

    fixtures = ['dump.json']


class BaseCartSeleniumTestCase(SeleniumTestCase):
    """Contains only cart actions set, but no tests."""

    def get_page(self, url: str) -> str:
        """Get page with selenium by given url."""
        url = urljoin(self.live_server_url, url)
        return self.browser.get(url)

    def buy_on_product_page(
        self, *, option: stb_models.Option=None, quantity=None, waiting_time=1
    ):
        option = option or stb_models.Option.objects.first()
        self.get_page(option.url)

        if quantity:
            self.send_keys_and_wait(
                quantity,
                (By.CSS_SELECTOR, f'tr[data-id="{option.id}"] .table-count-input'),
            )

        self.click_and_wait(
            (By.CSS_SELECTOR, f'button[data-id="{option.id}"]'),
            EC.visibility_of_element_located((By.CLASS_NAME, 'cart')),
        )

    def buy_on_category_page(self, wait=True):
        self.wait.until(EC.element_to_be_clickable(
            (By.CLASS_NAME, 'js-category-buy')
        ))
        buy_button = self.browser.find_element_by_class_name('js-category-buy')
        buy_button.click()
        if wait:
            self.wait.until(EC.visibility_of_element_located(
                (By.CLASS_NAME, 'js-cart')
            ))

    def cart(self):
        return self.browser.find_element_by_class_name('cart-wrapper')

    def show_cart(self):
        hover(self.browser, self.cart())
        self.wait.until(EC.visibility_of_element_located(
            (By.CLASS_NAME, 'cart')
        ))

    def positions(self, browser=None):
        browser = browser or self.browser
        return browser.find_elements_by_class_name('cart-item')

    def positions_count(self):
        self.show_cart()
        return len(self.positions())


@tag('slow', 'cart')
class HeaderCart(BaseCartSeleniumTestCase):

    def setUp(self):
        super(HeaderCart, self).setUp()
        self.browser.get(self.live_server_url)

    def assert_cart_is_empty(self):
        self.show_cart()
        cart_list = self.browser.find_element_by_class_name('js-cart').text

        self.assertIn('В корзине пока нет товаров', cart_list)

    def test_empty_cart_dropdown(self):
        self.assert_cart_is_empty()

    def test_add_to_cart_updates_header(self):
        self.buy_on_product_page()

        self.assertEqual(self.positions_count(), 1)

        product_in_database = stb_models.Product.objects.get(id=1).name
        product_in_cart_name = self.browser.find_element_by_class_name('cart-item-name').text

        self.assertEqual(product_in_database, product_in_cart_name)

    def test_delete_from_header_cart(self):
        self.buy_on_product_page()
        self.buy_on_product_page(option=stb_models.Option.objects.all()[2])
        self.show_cart()

        def wait_reducing(browser):
            return before_count > len(browser.find_elements_by_class_name('cart-item'))

        before_count = self.positions_count()
        self.click_and_wait(
            (By.CLASS_NAME, 'js-remove'), wait_reducing
        )
        self.assertEqual(self.positions_count(), 1)

    def test_flush_cart(self):
        self.buy_on_product_page()
        self.buy_on_product_page(option=stb_models.Option.objects.all()[2])
        self.show_cart()
        self.click_and_wait(
            (By.CLASS_NAME, 'js-flush-cart'),
            EC.presence_of_element_located((By.CLASS_NAME, 'cart-empty-text')),
        )
        self.assert_cart_is_empty()


@tag('slow', 'cart')
class ProductPage(BaseCartSeleniumTestCase):

    def test_buy_product(self):
        self.buy_on_product_page()

        self.assertEqual(self.positions_count(), 1)

    def test_buy_two_products(self):
        self.buy_on_product_page()
        self.buy_on_product_page(option=stb_models.Option.objects.all()[2])

        self.assertEqual(self.positions_count(), 2)

    def test_buy_product_with_count(self):
        self.buy_on_product_page(quantity=42)
        self.show_cart()

        self.assertIn('42', header_product_count(self))

    def test_buy_the_last_option(self):
        """The last option should have working "order" button."""
        product = stb_models.Product.objects.first()
        self.get_page(product.url)
        row = self.wait.until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, '.options-table tr:last-child')
            )
        )
        option = stb_models.Option.objects.get(
            id=int(row.get_attribute('data-id'))
        )
        self.buy_on_product_page(quantity=42, option=option)
        self.show_cart()

        self.assertIn('42', header_product_count(self))


@tag('slow', 'cart')
class OrderPage(BaseCartSeleniumTestCase):

    def setUp(self):
        super().setUp()
        self.product_row = 'js-product-row'
        self.product_remove = 'order-icon-remove'

    def remove_product(self):
        # delete first product in table
        to_delete = self.wait.until(EC.element_to_be_clickable(
            (By.CLASS_NAME, self.product_remove)
        ))
        to_delete.click()
        self.wait.until(EC.staleness_of(to_delete))

    def proceed_order_page(self):
        self.browser.get(
            self.live_server_url +
            reverse_custom_page('order')
        )
        self.wait.until(EC.visibility_of_element_located(
            (By.TAG_NAME, 'h1')
        ))

    def get_total(self, browser=None):
        browser = browser or self.browser
        return browser.find_element_by_class_name('order-total-val').text

    def test_order_page_actual_count_of_rows(self):
        self.buy_on_product_page()
        self.buy_on_product_page(option=stb_models.Option.objects.all()[2])
        self.proceed_order_page()

        products_in_table = self.browser.find_elements_by_class_name(self.product_row)
        self.assertEqual(len(products_in_table), 2)

    def test_order_page_remove_row(self):
        self.buy_on_product_page()
        self.buy_on_product_page(option=stb_models.Option.objects.all()[2])
        self.proceed_order_page()

        self.remove_product()
        products_in_table = self.browser.find_elements_by_class_name(self.product_row)

        self.assertEqual(len(products_in_table), 1)

    def test_order_page_remove_all_products(self):
        self.buy_on_product_page()
        self.proceed_order_page()

        self.remove_product()
        order_wrapper_text = self.browser.find_element_by_class_name('js-order-contain').text

        self.assertIn('Нет выбранных позиций', order_wrapper_text)

    def test_change_count_in_cart(self):
        option = stb_models.Option.objects.first()
        self.buy_on_product_page(option=option)
        self.proceed_order_page()

        count = 42
        total_before = self.get_total()

        def wait_total_changed(driver):
            return self.get_total(driver) != total_before

        self.send_keys_and_wait(count, (By.CLASS_NAME, 'js-count-input'))
        self.wait.until(wait_total_changed)

        self.assertEqual(
            f'{floatformat(str(option.price * count), 0)} руб',
            self.get_total(),
        )

    @test_helpers.disable_celery
    def test_order_email(self):
        option = stb_models.Option.objects.first()
        self.buy_on_product_page(option=option)
        self.proceed_order_page()

        # @todo #137 Setting a number of items flush all other fields on order page.
        #  Steps to reproduce the bug:
        #  1. Add products to a cart and open an order page
        #  2. Fill the fields (name, email, phone, etc.)
        #  2. Change the number of any item

        # self.send_keys_and_wait(
        #     42, (By.CLASS_NAME, 'js-count-input'),
        # )
        total_price = self.get_total()
        expected_phone = '+2 (222) 222 22 22'
        customer_data = [
            ('id_name', 'Name'), ('id_email', 'test@test.test'), ('id_company', 'Some Company'),
            ('id_address', 'Санкт-Петербург'), ('id_comment', 'Some comment')
        ]

        for element, value in customer_data:
            self.send_keys_and_wait(value, (By.ID, element))
        self.send_keys_and_wait('22222222222', (By.ID, 'id_phone'), expected_phone)

        self.click_and_wait(
            (By.CSS_SELECTOR, '.btn-order-form .btn'),
            EC.text_to_be_present_in_element(
                (By.TAG_NAME, 'h1'), 'Ваш заказ принят'
            ),
        )

        sent_mail_body = mail.outbox[0].body

        self.assertInHTML(
            '<td style="border-color:#E4E4E4;padding:10px">'
            f'{option.code or ""}</td>',
            sent_mail_body
        )
        self.assertIn(
            f'<a href="{ settings.BASE_URL }{option.url}"',
            sent_mail_body
        )
        self.assertInHTML(total_price, sent_mail_body)

        for _, html_chunk in customer_data:
            self.assertInHTML(f'<b>{html_chunk}</b>', sent_mail_body)
        self.assertInHTML(f'<b>{expected_phone}</b>', sent_mail_body)


@tag('slow', 'cart')
class CategoryPage(BaseCartSeleniumTestCase, test_helpers.CategoryTestMixin):

    PRODUCTS_TO_LOAD = 30
    SELENIUM_TIMEOUT = 60
    CATEGORY_ROUTE_NAME = 'category'
    APPLY_BTN_CLASS = 'js-apply-filter'
    TAG_ID_TEMPLATE = 'tag-{tag_slug}'
    QUANTITY_CLASS = 'js-count-input'
    LOAD_MORE_ID = 'load-more-products'
    FILTER_ID = 'search-filter'

    def setUp(self):
        # CI always have problems with CategoryPage timeouts
        self.browser.set_page_load_timeout(self.SELENIUM_TIMEOUT)
        self.browser.set_script_timeout(self.SELENIUM_TIMEOUT)
        self.root_category = stb_models.Category.objects.filter(parent=None).first()
        self.middle_category = stb_models.Category.objects.get(name='Category #0 of #1')

    def load_category_page(
        self,
        category: stb_models.Category=None,
        tags: stb_models.TagQuerySet=None,
        sorting: int=None,
        query_string: dict=None,
    ):
        category = category or self.root_category
        route_name = self.CATEGORY_ROUTE_NAME
        category_url = self.live_server_url + self.get_category_path(
            category, route_name, tags, sorting, query_string
        )
        self.browser.get(category_url)
        self.wait_page_loading()

    def wait_page_loading(self):
        wait_page_loading(self.browser)

    def get_tables_rows_count(self, browser=None):
        browser = browser or self.browser
        return len(browser.find_elements_by_class_name('table-tr'))

    def click_load_more_button(self):
        count = self.get_tables_rows_count()
        self.click_and_wait(
            (By.ID, self.LOAD_MORE_ID),
            lambda browser: self.get_tables_rows_count(browser) > count
        )

    def get_loaded_products_count(self):
        return (
            self.browser
            .find_element_by_id(self.LOAD_MORE_ID)
            .get_attribute('data-total-products')
        )

    def is_load_more_disabled(self, browser=None):
        browser = browser or self.browser
        return 'disabled' in (
            browser
            .find_element_by_id(self.LOAD_MORE_ID)
            .get_attribute('class')
        )

    def apply_tags(self):
        """Push "apply" button with trailing page reloading."""
        old_url = self.browser.current_url
        self.browser.find_element_by_class_name(self.APPLY_BTN_CLASS).click()
        self.wait.until(EC.url_changes(old_url))
        self.wait_page_loading()

    @staticmethod
    def get_first_tag(category: stb_models.Category):
        return stb_models.Tag.objects.filter_by_options(
            options=stb_models.Option.objects.filter_descendants(category)
        ).first()

    def test_buy_product(self):
        self.load_category_page()
        self.buy_on_category_page()
        self.assertEqual(self.positions_count(), 1)

    def test_buy_two_product(self):
        self.load_category_page()
        self.buy_on_category_page()
        self.wait.until(EC.invisibility_of_element_located(
            (By.CLASS_NAME, 'js-cart')
        ))
        self.buy_on_category_page()

        self.assertIn('2', header_product_count(self))

    def test_buy_product_with_quantity(self):
        self.load_category_page()
        self.send_keys_and_wait(42, (By.CLASS_NAME, self.QUANTITY_CLASS))
        self.buy_on_category_page()

        self.assertEqual(self.positions_count(), 1)
        self.assertIn('42', header_product_count(self))

    def test_category_tooltip(self):
        """We should see tooltip after clicking on `Заказать` button."""
        self.load_category_page()
        tooltip = self.browser.find_element_by_class_name('js-popover')
        self.buy_on_category_page()
        self.assertTrue(tooltip.is_displayed())

    def test_load_more_products(self):
        """We able to load more products by clicking on `Load more` link."""
        self.load_category_page()

        before_load_products = self.get_tables_rows_count()
        self.click_load_more_button()
        after_load_products = self.get_tables_rows_count()

        self.assertTrue(before_load_products < after_load_products)

    @staticmethod
    def get_category_with_options_limit(low: int, high: int):
        """Return the first category having only one load_more click."""
        return next(iter(
            stb_models.Category.objects.raw(
                '''
                SELECT cat.id FROM stroyprombeton_category as cat
                INNER JOIN stroyprombeton_product as prod ON prod.category_id = cat.id
                INNER JOIN stroyprombeton_option as opt ON opt.product_id = prod.id
                GROUP BY cat.id
                HAVING COUNT(*) > %s AND COUNT(*) < %s;
                ''',
                [low, high]
            )
        ))

    def test_load_more_button_disabled_state(self):
        """
        Test the load more lint state.

        If we filter products and load more products several times - we should
        see that `Load more` link becomes disabled. That means that there are
        no more filtered products to load from server.
        """
        per_page = request_data.Category.PRODUCTS_ON_PAGE_PC
        self.load_category_page(
            self.get_category_with_options_limit(
                low=per_page, high=2 * per_page
            )
        )
        self.send_keys_and_wait('#1', (By.ID, self.FILTER_ID))
        self.click_load_more_button()
        self.assertTrue(self.is_load_more_disabled())

    @unittest.expectedFailure
    def test_load_more_button_disabled_state_with_few_products(self):
        """
        Test the load more link state.

        `Load more` link should be disabled by default if there are less
        than PRODUCTS_TO_LOAD products on page.
        """
        # @todo #675:30m  At the fixtures create category with a few options.
        #  "A few options" means with less then options per_page limit count.
        #  See the code below.

        per_page = request_data.Category.PRODUCTS_ON_PAGE_PC
        self.load_category_page(
            self.get_category_with_options_limit(
                low=0, high=per_page
            )
        )
        self.assertTrue(self.is_load_more_disabled())

    # @todo #419:30m  Create fast search tests.
    def test_filter_products(self):
        """We are able to filter products by typing in filter field."""
        def wait_filter(browser):
            return self.is_load_more_disabled(browser)

        self.load_category_page()

        before_filter_products = self.get_tables_rows_count()
        self.send_keys_and_wait('#10', (By.ID, self.FILTER_ID))
        self.wait.until(wait_filter)
        after_filter_products = self.get_tables_rows_count()

        self.assertGreater(before_filter_products, after_filter_products)

    def test_tag_button_change_url(self):
        """Filter button with the filled one of tag checkboxes should change url to tag."""
        # set one product with no tags in test_db
        # check if this prod is not in list after filtering
        self.load_category_page(self.middle_category)  # Ignore CPDBear
        tag = self.get_first_tag(self.middle_category)
        tag_selector = self.TAG_ID_TEMPLATE.format(tag_slug=tag.slug)

        self.browser.find_element_by_id(tag_selector).click()
        self.apply_tags()
        tagged_category_path = self.get_category_path(
            category=self.middle_category,
            tags=stb_models.Tag.objects.filter(slug=tag.slug)
        )
        self.assertIn(tagged_category_path, self.browser.current_url)
        self.browser.find_element_by_class_name('js-clear-tag-filter').click()

    def test_tag_button_filter_products(self):
        # this category contains 25 tags. It's less then products on page limit.
        category = stb_models.Category.objects.get(name='Category #1 of #2')
        tag = self.get_first_tag(category)
        tag_selector = self.TAG_ID_TEMPLATE.format(tag_slug=tag.slug)
        self.load_category_page(category)
        before_products_count = self.get_loaded_products_count()

        self.browser.find_element_by_id(tag_selector).click()
        self.apply_tags()

        after_products_count = self.get_loaded_products_count()
        self.assertGreater(int(before_products_count), int(after_products_count))

        self.browser.find_element_by_class_name('js-clear-tag-filter').click()
        after_products_count = self.get_loaded_products_count()
        self.assertEqual(int(before_products_count), int(after_products_count))

    def test_flush_button(self):
        category = self.root_category
        self.load_category_page(
            category=category,
            tags=stb_models.Tag.objects.filter(slug='2-m')
        )
        self.browser.find_element_by_class_name('js-clear-tag-filter').click()
        self.wait_page_loading()
        # category with no tags
        category_url = self.live_server_url + self.get_category_path(category)
        self.assertEqual(category_url, self.browser.current_url)

    def test_apply_filter_state(self):
        """Apply filters btn should be disabled with no checked tags."""
        self.load_category_page(self.middle_category)
        tag = self.get_first_tag(self.middle_category)
        tag_selector = self.TAG_ID_TEMPLATE.format(tag_slug=tag.slug)

        is_button_disabled = bool(
            self.browser
            .find_element_by_class_name(self.APPLY_BTN_CLASS)
            .get_attribute('disabled')
        )
        self.assertTrue(is_button_disabled)

        self.browser.find_element_by_id(tag_selector).click()
        is_button_disabled = bool(
            self.browser
            .find_element_by_class_name(self.APPLY_BTN_CLASS)
            .get_attribute('disabled')
        )
        self.assertFalse(is_button_disabled)

    def test_hidden_pagination(self):
        self.load_category_page()
        pagination = self.browser.find_element_by_class_name('js-seo-links')
        self.assertFalse(pagination.is_displayed())


@tag('slow')
class Search(SeleniumTestCase):
    """Selenium-based tests for Search."""

    INPUT_LOCATOR = (By.CLASS_NAME, 'js-search-field')

    def setUp(self):
        self.browser.get(self.live_server_url)
        # query contains whitespace to prevent urlencoding errors
        self.query = 'category'
        self.wrong_query = 'Not existing search query'
        self.search_url = '/search/'

    @property
    def autocomplete(self):
        return self.wait.until(EC.presence_of_element_located(
            (By.CLASS_NAME, 'autocomplete-suggestions')
        ))

    @property
    def input(self):
        return self.wait.until(EC.visibility_of_element_located(
            self.INPUT_LOCATOR
        ))

    def search_loaded_condition(self):
        return EC.url_contains(self.search_url)

    def fill_input(self, query=''):
        """Enter correct search term."""
        self.send_keys_and_wait(query or self.query, self.INPUT_LOCATOR)

    def fill_input_and_wait(self, query=''):
        self.fill_input(query)
        self.wait.until(EC.visibility_of(self.autocomplete))

    def search(self, query=''):
        self.fill_input(query)
        self.click_and_wait(
            (By.CLASS_NAME, 'search-btn'),
            self.search_loaded_condition(),
        )

    # fix it with #359
    @unittest.skip
    def test_autocomplete_can_expand_and_collapse(self):
        """
        Test the autocomplete behavior.

        Autocomplete should minimize during user typing correct search query
        Autocomplete should minimize by removing search query.
        """
        self.fill_input_and_wait()
        # input was filled, so autocomplete should expand
        self.assertTrue(self.autocomplete.is_displayed())

        # remove search term ...
        self.input.clear()
        self.wait.until_not(EC.visibility_of(self.autocomplete))

        # ... and autocomplete should collapse
        self.assertFalse(self.autocomplete.is_displayed())

    # @todo #205:30m  Resurrect `test_autocomplete_item_link`
    @unittest.skip
    def test_autocomplete_item_link(self):
        """Every autocomplete item should contain link on page."""
        self.fill_input_and_wait()
        self.autocomplete.find_element_by_class_name('autocomplete-suggestion').click()

        self.wait.until(EC.url_contains('/gbi/products/'))
        self.assertTrue('/gbi/products/' in self.browser.current_url)

    @unittest.skip
    def test_autocomplete_see_all_item(self):
        """
        Autocomplete should contain "see all" item.

        "See all" item links on search results page.
        """
        self.fill_input_and_wait()
        self.click_and_wait(
            (By.CLASS_NAME, 'search-more-link'),
            self.search_loaded_condition(),
        )

        self.assertTrue(self.search_url in self.browser.current_url)

    def test_search_have_results(self):
        """Search results page should contain links on relevant pages."""
        query = 'Product #10'
        self.search(query)
        product = stb_models.Product.objects.filter(name__startswith=query).first()
        self.assertTrue(
            self.browser.find_element_by_link_text(
                product.name
            )
        )

    def test_search_results_empty(self):
        """Search results for wrong term should contain empty result set."""
        self.search(query=self.wrong_query)

        h1 = self.browser.find_element_by_tag_name('h1')
        self.assertTrue(h1.text == 'По вашему запросу ничего не найдено')

    @unittest.skip
    def test_autocomplete_results_empty(self):
        """Autocomplete does not display for wrong query."""
        self.fill_input(query=self.wrong_query)

        self.assertFalse(self.autocomplete.is_displayed())

    def test_autocomplete_for_product(self):
        """Autocomplete suggests products."""
        self.fill_input(query='product')
        suggestion = self.wait.until(EC.visibility_of_element_located(
            (By.CLASS_NAME, 'autocomplete-suggestion'),
        ))

        self.assertTrue(
            suggestion.text.startswith('Product'),
            suggestion.text,
        )


@tag('slow')
class IndexPage(SeleniumTestCase):

    def setUp(self):
        super().setUp()
        self.browser.get(self.live_server_url)

    def fill_and_send_backcall_request_form(self):
        self.browser.execute_script('$("#id_name").val("");')
        self.browser.execute_script('$("#id_phone").val("");')

        self.browser.find_element_by_id('id_name')
        self.browser.find_element_by_id('id_phone')

        self.send_keys_and_wait('Yo', (By.ID, 'id_name'))
        self.send_keys_and_wait('22222222222', (By.ID, 'id_phone'), '+2 (222) 222 22 22')

        self.click_and_wait(
            (By.CLASS_NAME, 'js-send-backcall'),
            EC.invisibility_of_element_located((By.CLASS_NAME, 'js-modal')),
        )

    def test_backcall_request(self):
        self.wait.until(EC.element_to_be_clickable((
            (By.CLASS_NAME, 'js-open-modal')
        ))).click()
        modal = self.wait.until(EC.visibility_of_element_located(
            (By.CLASS_NAME, 'js-modal')
        ))
        send_btn = self.browser.find_element_by_class_name('js-send-backcall')

        self.assertTrue(modal.is_displayed())

        self.fill_and_send_backcall_request_form()

        self.assertTrue(send_btn.get_attribute('disabled'))
        self.assertFalse(modal.is_displayed())

    @test_helpers.disable_celery
    def test_backcall_request_email(self):
        """Back call email should contains input name and phone number."""
        self.browser.find_element_by_class_name('js-open-modal').click()
        self.fill_and_send_backcall_request_form()

        sent_mail_body = mail.outbox[0].body

        self.assertIn('name: Yo', sent_mail_body)
        self.assertIn('phone: +2 (222) 222 22 22', sent_mail_body)
