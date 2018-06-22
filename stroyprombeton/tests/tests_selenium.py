import unittest

from django.core import mail
from django.db.models import Count
from django.template.defaultfilters import floatformat
from django.urls import reverse
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.models import Page

from stroyprombeton.models import Category, Product
from stroyprombeton.tests.helpers import disable_celery, BaseSeleniumTestCase


def hover(browser, element):
    """Perform a hover over an element."""
    hover_action = ActionChains(browser).move_to_element(element)
    hover_action.perform()


def header_product_count(self):
    element = self.wait.until(EC.visibility_of_element_located(
        (By.CLASS_NAME, 'js-header-product-count')
    ))
    return element.text


class SeleniumTestCase(BaseSeleniumTestCase):
    """Common superclass for running selenium-based tests."""

    fixtures = ['dump.json']


class CartTestCase(SeleniumTestCase):

    def buy_on_product_page(self, *, product_id=1, quantity=None, waiting_time=1):
        product_page = (self.live_server_url + reverse('product', args=(product_id,)))
        self.browser.get(product_page)

        if quantity:
            self.send_keys_and_wait(
                quantity,
                (By.CLASS_NAME, 'js-count-input'),
            )

        self.click_and_wait(
            (By.ID, 'buy-product'),
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


class HeaderCart(CartTestCase):

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

        product_in_database = Product.objects.get(id=1).name
        product_in_cart_name = self.browser.find_element_by_class_name('cart-item-name').text

        self.assertEqual(product_in_database, product_in_cart_name)

    def test_delete_from_header_cart(self):
        self.buy_on_product_page()
        self.buy_on_product_page(product_id=2)
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
        self.buy_on_product_page(product_id=2)
        self.show_cart()
        self.click_and_wait(
            (By.CLASS_NAME, 'js-flush-cart'),
            EC.presence_of_element_located((By.CLASS_NAME, 'cart-empty-text')),
        )
        self.assert_cart_is_empty()


class ProductPage(CartTestCase):

    def test_buy_product(self):
        self.buy_on_product_page()

        self.assertEqual(self.positions_count(), 1)

    def test_buy_two_products(self):
        self.buy_on_product_page()
        self.buy_on_product_page(product_id=2)

        self.assertEqual(self.positions_count(), 2)

    def test_buy_product_with_count(self):
        self.buy_on_product_page(quantity=42)
        self.show_cart()

        self.assertIn('42', header_product_count(self))


class OrderPage(CartTestCase):

    def setUp(self):
        super().setUp()
        self.product_row = 'js-product-row'
        self.product_remove = 'order-icon-remove'

    def remove_product(self):
        def wait_reducing(browser):
            return before_count > len(browser.find_elements_by_class_name(self.product_row))

        before_count = len(self.browser.find_elements_by_class_name(self.product_row))
        # delete first product in table
        self.click_and_wait((By.CLASS_NAME, self.product_remove), wait_reducing)

    def proceed_order_page(self):
        self.browser.get(
            self.live_server_url +
            reverse(Page.CUSTOM_PAGES_URL_NAME, args=('order', ))
        )
        self.wait.until(EC.visibility_of_element_located(
            (By.TAG_NAME, 'h1')
        ))

    def get_total(self, browser=None):
        browser = browser or self.browser
        return browser.find_element_by_class_name('order-total-val').text

    def test_order_page_actual_count_of_rows(self):
        self.buy_on_product_page()
        self.buy_on_product_page(product_id=2)
        self.proceed_order_page()

        products_in_table = self.browser.find_elements_by_class_name(self.product_row)
        self.assertEqual(len(products_in_table), 2)

    def test_order_page_remove_row(self):
        self.buy_on_product_page()
        self.buy_on_product_page(product_id=2)
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

    # @todo #200:30m Fix test_change_count_in_cart test.
    #  Traceback: https://ci.fidals.com/fidals/stroyprombeton/72/8
    @unittest.expectedFailure
    def test_change_count_in_cart(self):
        self.buy_on_product_page()
        self.proceed_order_page()

        total = self.get_total()

        def wait_total_changes(driver):
            return self.get_total(driver) != total

        self.send_keys_and_wait(42, (By.CLASS_NAME, 'js-count-input'))
        self.wait.until(wait_total_changes)
        product_price = Product.objects.get(id=1).price
        expected_price = floatformat(str(product_price * 42), 0) + ' руб'
        total_price = self.get_total()

        self.assertEqual(expected_price, total_price)

    @disable_celery
    def test_order_email(self):
        self.buy_on_product_page()
        self.proceed_order_page()

        code = Product.objects.get(id=1).code

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
            '<td style="border-color:#E4E4E4;padding:10px">{0}</td>'
            .format(str(code)),
            sent_mail_body
        )
        self.assertIn(
            '<a href="http://www.stroyprombeton.ru{0}"'
            .format(reverse('product', args=(1,))),
            sent_mail_body
        )
        self.assertInHTML(
            '<td style="border-color:#E4E4E4;padding:10px;font-weight:bold">{0}</td>'
            .format(total_price),
            sent_mail_body
        )

        for _, html_chunk in customer_data:
            self.assertInHTML(f'<b>{html_chunk}</b>', sent_mail_body)
        self.assertInHTML(f'<b>{expected_phone}</b>', sent_mail_body)


class CategoryPage(CartTestCase):

    PRODUCTS_TO_LOAD = 30
    SELENIUM_TIMEOUT = 60

    @classmethod
    def setUpClass(cls):
        super(CategoryPage, cls).setUpClass()
        cls.quantity_class = 'js-count-input'
        cls.load_more_id = 'load-more-products'
        cls.filter_id = 'search-filter'

    def setUp(self):
        def testing_url(category_id):
            return server + reverse('category', args=(category_id,))

        server = self.live_server_url
        # CI always have problems with CategoryPage timeouts
        self.browser.set_page_load_timeout(self.SELENIUM_TIMEOUT)
        self.browser.set_script_timeout(self.SELENIUM_TIMEOUT)
        root_category = Category.objects.filter(parent=None).first()
        children_category = Category.objects.filter(parent=root_category).first()
        category_with_product_less_then_load_limit = Category.objects.annotate(
            prod_count=Count('products')).exclude(prod_count=0).filter(
                prod_count__lt=self.PRODUCTS_TO_LOAD).first()

        self.root_category = testing_url(root_category.id)
        self.children_category = testing_url(children_category.id)
        self.deep_children_category = testing_url(
            category_with_product_less_then_load_limit.id
        )
        self.browser.get(self.root_category)
        self.wait.until(EC.visibility_of_element_located((By.TAG_NAME, 'h1')))

    def get_tables_rows_count(self, browser=None):
        browser = browser or self.browser
        return len(browser.find_elements_by_class_name('table-tr'))

    def click_load_more_button(self):
        def wait_loading(browser):
            return product_count < self.get_tables_rows_count(browser)
        product_count = self.get_tables_rows_count()
        self.click_and_wait((By.ID, self.load_more_id), wait_loading)

    def get_load_more_button_classes(self, browser=None):
        browser = browser or self.browser
        return browser.find_element_by_id(self.load_more_id).get_attribute('class')

    def test_buy_product(self):
        self.buy_on_category_page()

        self.assertEqual(self.positions_count(), 1)

    def test_buy_two_product(self):
        self.buy_on_category_page()
        self.wait.until(EC.invisibility_of_element_located(
            (By.CLASS_NAME, 'js-cart')
        ))
        self.buy_on_category_page()

        self.assertIn('2', header_product_count(self))

    def test_buy_product_with_quantity(self):
        self.send_keys_and_wait(42, (By.CLASS_NAME, self.quantity_class))
        self.buy_on_category_page()

        self.assertEqual(self.positions_count(), 1)
        self.assertIn('42', header_product_count(self))

    def test_category_tooltip(self):
        """We should see tooltip after clicking on `Заказать` button."""
        tooltip = self.browser.find_element_by_class_name('js-popover')
        self.buy_on_category_page()

        self.assertTrue(tooltip.is_displayed())

    def test_load_more_products(self):
        """We able to load more products by clicking on `Load more` link."""
        before_load_products = self.get_tables_rows_count()
        self.click_load_more_button()
        after_load_products = self.get_tables_rows_count()

        self.assertTrue(before_load_products < after_load_products)

    def test_load_more_button_disabled_state_with_few_products(self):
        """
        Test the load more link state.

        `Load more` link should be disabled by default if there are less
        than PRODUCTS_TO_LOAD products on page.
        """
        self.browser.get(self.deep_children_category)

        self.assertIn('disabled', self.get_load_more_button_classes())

    def test_load_more_button_disabled_state(self):
        self.browser.get(self.children_category)
        self.click_load_more_button()
        self.click_load_more_button()

        self.assertIn('disabled', self.get_load_more_button_classes())

    def test_filter_products(self):
        """We are able to filter products by typing in filter field."""
        def wait_filter(browser):
            return 'disabled' in self.get_load_more_button_classes(browser)

        before_filter_products = self.get_tables_rows_count()
        self.send_keys_and_wait('#10', (By.ID, self.filter_id))
        self.wait.until(wait_filter)
        after_filter_products = self.get_tables_rows_count()

        self.assertGreater(before_filter_products, after_filter_products)

    def test_filter_products_and_disabled_state(self):
        """
        Test the load more lint state.

        If we filter products and load more products several times - we should
        see that `Load more` link becomes disabled. That means that there are
        no more filtered products to load from server.
        """
        self.send_keys_and_wait('#1', (By.ID, self.filter_id))
        self.click_load_more_button()
        self.click_load_more_button()

        self.assertIn('disabled', self.get_load_more_button_classes())


class Search(SeleniumTestCase):
    """Selenium-based tests for Search."""

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

    def search_loaded_condition(self):
        return EC.url_contains(self.search_url)

    def clear_input(self, number):
        self.wait.until(EC.visibility_of_element_located(
            (By.CLASS_NAME, 'js-search-field')
        )).send_keys(Keys.BACKSPACE * number)
        self.wait.until_not(EC.visibility_of(self.autocomplete))

    def fill_input(self, query=''):
        """Enter correct search term."""
        self.send_keys_and_wait(query or self.query, (By.CLASS_NAME, 'js-search-field'))

    def fill_input_and_wait(self, query=''):
        self.fill_input(query)
        self.wait.until(EC.visibility_of(self.autocomplete))

    def search(self, query=''):
        self.fill_input(query)
        self.click_and_wait(
            (By.CLASS_NAME, 'search-btn'),
            self.search_loaded_condition(),
        )

    # @todo #142:30m Resurrect test for expanding of autocomplete
    @unittest.skip('Fix after se#344 resolving.')
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
        self.clear_input(len(self.query))

        # ... and autocomplete should collapse
        self.assertFalse(self.autocomplete.is_displayed())

    # @todo #380:30m Resurrect test `test_autocomplete_item_link`
    @unittest.skip
    def test_autocomplete_item_link(self):
        """Every autocomplete item should contain link on page."""
        self.fill_input_and_wait()
        self.autocomplete.find_element_by_class_name('autocomplete-suggestion').click()

        self.wait.until(EC.url_contains('/gbi/products/'))
        self.assertTrue('/gbi/products/' in self.browser.current_url)

    # @todo #142:15m Resurrect test for see all link of autocomplete
    @unittest.skip('Fix after se#344 resolving.')
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
        self.search()

        self.assertTrue(self.browser.find_element_by_link_text('Category root #0'))
        self.assertTrue(self.browser.find_element_by_link_text('Category #0 of #1'))

    def test_inactive_product_not_in_search_autocomplete(self):
        test_product = Product.objects.first()
        test_product.page.is_active = False
        test_product.page.save()
        self.fill_input(query=test_product.name)

        product_not_exist = EC.invisibility_of_element_located(
            (By.LINK_TEXT, test_product.url)
        )
        self.assertTrue(product_not_exist(self.browser))

    def test_search_results_empty(self):
        """Search results for wrong term should contain empty result set."""
        self.search(query=self.wrong_query)

        h1 = self.browser.find_element_by_tag_name('h1')
        self.assertTrue(h1.text == 'По вашему запросу ничего не найдено')

    def test_autocomplete_results_empty(self):
        """Autocomplete does not display for wrong query."""
        self.fill_input(query=self.wrong_query)

        self.assertFalse(self.autocomplete.is_displayed())


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

    @disable_celery
    def test_backcall_request_email(self):
        """Back call email should contains input name and phone number."""
        self.browser.find_element_by_class_name('js-open-modal').click()
        self.fill_and_send_backcall_request_form()

        sent_mail_body = mail.outbox[0].body

        self.assertIn('name: Yo', sent_mail_body)
        self.assertIn('phone: +2 (222) 222 22 22', sent_mail_body)
