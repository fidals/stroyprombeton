from django.core import mail
from django.db.models import Count
from django.template.defaultfilters import floatformat
from django.urls import reverse
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement

from pages.models import Page

from stroyprombeton.models import Category, Product
from stroyprombeton.tests.helpers import wait, disable_celery, BaseSeleniumTestCase


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


class Action(WebElement):
    @classmethod
    def click_and_wait(cls, element, waiting_time=1):
        element.click()
        wait(waiting_time)

    @classmethod
    def send_keys_and_wait(cls, element, *value, waiting_time=1):
        element.send_keys(*value)
        wait(waiting_time)


click_and_wait = Action.click_and_wait
send_keys_and_wait = Action.send_keys_and_wait


class CartMixin:
    def buy_on_product_page(self, *, product_id=1, quantity=None, waiting_time=1):
        product_page = (self.live_server_url + reverse('product', args=(product_id,)))
        self.browser.get(product_page)

        if quantity:
            q = self.browser.find_element_by_class_name('js-count-input')
            q.clear()
            send_keys_and_wait(q, quantity, waiting_time=waiting_time)

        click_and_wait(self.browser.find_element_by_id('buy-product'), waiting_time=waiting_time)

    def buy_on_category_page(self, waiting_time=1):
        click_and_wait(self.browser.find_element_by_class_name('js-category-buy'), waiting_time)

    def cart(self):
        return self.browser.find_element_by_class_name('cart-wrapper')

    def show_cart(self):
        hover(self.browser, self.cart())
        self.wait.until(EC.visibility_of_element_located(
            (By.CLASS_NAME, 'cart')
        ))

    def positions(self):
        return self.browser.find_elements_by_class_name('cart-item')

    def positions_count(self):
        self.show_cart()
        return len(self.positions())


class HeaderCart(SeleniumTestCase, CartMixin):
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
        click_and_wait(self.browser.find_element_by_class_name('js-remove'))

        self.assertEqual(self.positions_count(), 1)

    def test_flush_cart(self):
        self.buy_on_product_page()
        self.buy_on_product_page(product_id=2)
        self.show_cart()
        click_and_wait(self.browser.find_element_by_class_name('js-flush-cart'))

        self.assert_cart_is_empty()


class ProductPage(SeleniumTestCase, CartMixin):
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


class OrderPage(SeleniumTestCase, CartMixin):
    def setUp(self):
        super(OrderPage, self).setUp()
        self.product_row = 'js-product-row'
        self.product_remove = 'js-remove'

    def proceed_order_page(self):
        self.browser.get(
            self.live_server_url +
            reverse(Page.CUSTOM_PAGES_URL_NAME, args=('order', ))
        )

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

        product_row = self.browser.find_element_by_class_name(self.product_row)
        click_and_wait(product_row.find_element_by_class_name(self.product_remove))
        products_in_table = self.browser.find_elements_by_class_name(self.product_row)

        self.assertEqual(len(products_in_table), 1)

    def test_order_page_remove_all_products(self):
        self.buy_on_product_page()
        self.proceed_order_page()

        product_row = self.browser.find_element_by_class_name(self.product_row)
        click_and_wait(product_row.find_element_by_class_name(self.product_remove))
        order_wrapper_text = self.browser.find_element_by_class_name('js-order-contain').text

        self.assertIn('Нет выбранных позиций', order_wrapper_text)

    def test_change_count_in_cart(self):
        self.buy_on_product_page()
        self.proceed_order_page()

        counter = self.browser.find_element_by_class_name('js-count-input')
        counter.clear()
        send_keys_and_wait(counter, 42)
        product_price = Product.objects.get(id=1).price
        expected_price = floatformat(str(product_price * 42), 0) + ' руб'
        total_price = self.browser.find_element_by_class_name('order-total-val').text

        self.assertEqual(expected_price, total_price)

    @disable_celery
    def test_order_email(self):
        self.buy_on_product_page()
        self.proceed_order_page()

        code = Product.objects.get(id=1).code
        counter = self.browser.find_element_by_class_name('js-count-input')
        counter.clear()
        send_keys_and_wait(counter, 42)
        total_price = self.browser.find_element_by_class_name('order-total-val').text

        customer_data = [
            ('id_name', 'Name'), ('id_phone', '22222222222'),
            ('id_email', 'test@test.test'), ('id_company', 'Some Company'),
            ('id_address', 'Санкт-Петербург'), ('id_comment', 'Some comment')
        ]
        for element, value in customer_data:
            self.browser.find_element_by_id(element).send_keys(value)

        Action.click_and_wait(
            self.browser.find_element_by_css_selector('.btn-order-form .btn')
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

        to_check = ['<b>Name</b>', '<b>+2 (222) 222 22 22</b>',
                    '<b>test@test.test</b>', '<b>Some Company</b>',
                    '<b>Санкт-Петербург</b>', '<b>Some comment</b>']
        for html_chunk in to_check:
            self.assertInHTML(html_chunk, sent_mail_body)


class CategoryPage(SeleniumTestCase, CartMixin):

    PRODUCTS_TO_LOAD = 30

    @classmethod
    def setUpClass(cls):
        super(CategoryPage, cls).setUpClass()
        cls.quantity = 'js-count-input'

    def setUp(self):
        def testing_url(category_id):
            return server + reverse('category', args=(category_id,))

        server = self.live_server_url
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

    def get_tables_rows_count(self):
        return len(self.browser.find_elements_by_class_name('table-tr'))

    def get_load_more_button(self):
        return self.browser.find_element_by_id('load-more-products')

    def get_load_more_button_classes(self):
        return self.get_load_more_button().get_attribute('class')

    def test_buy_product(self):
        self.buy_on_category_page()

        self.assertEqual(self.positions_count(), 1)

    def test_buy_two_product(self):
        self.buy_on_category_page()
        self.buy_on_category_page()

        self.assertIn('2', header_product_count(self))

    def test_buy_product_with_quantity(self):
        first_product_count = self.browser.find_element_by_class_name(self.quantity)
        first_product_count.clear()
        send_keys_and_wait(first_product_count, '42')
        self.buy_on_category_page()

        self.assertEqual(self.positions_count(), 1)
        self.assertIn('42', header_product_count(self))

    def test_category_tooltip(self):
        """We should see tooltip after clicking on `Заказать` button."""
        tooltip = self.browser.find_element_by_class_name('js-popover')
        self.buy_on_category_page(waiting_time=0.5)

        self.assertTrue(tooltip.is_displayed())

    def test_load_more_products(self):
        """We able to load more products by clicking on `Load more` link."""
        before_load_products = self.get_tables_rows_count()
        click_and_wait(self.get_load_more_button())
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
        load_more_button = self.get_load_more_button()
        click_and_wait(load_more_button)
        click_and_wait(load_more_button)
        click_and_wait(load_more_button)

        self.assertIn('disabled', self.get_load_more_button_classes())

    def test_filter_products(self):
        """We are able to filter products by typing in filter field."""
        self.wait.until(EC.visibility_of_element_located(
            (By.ID, 'search-filter')
        ))
        filter_field = self.browser.find_element_by_id('search-filter')
        before_filter_products = self.get_tables_rows_count()
        send_keys_and_wait(filter_field, '#10')
        after_filter_products = self.get_tables_rows_count()

        self.assertTrue(before_filter_products > after_filter_products)

    def test_filter_products_and_disabled_state(self):
        """
        Test the load more lint state.

        If we filter products and load more products several times - we should
        see that `Load more` link becomes disabled. That means that there are
        no more filtered products to load from server.
        """
        filter_field = self.browser.find_element_by_id('search-filter')
        send_keys_and_wait(filter_field, '#10')

        load_more_button = self.get_load_more_button()
        click_and_wait(load_more_button)
        click_and_wait(load_more_button)

        self.assertIn('disabled', self.get_load_more_button_classes())


class Search(SeleniumTestCase):
    """Selenium-based tests for Search."""

    def setUp(self):
        self.browser.get(self.live_server_url)
        # query contains whitespace to prevent urlencoding errors
        self.query = 'category'
        self.fill_input()

    @property
    def autocomplete(self):
        return self.browser.find_element_by_class_name('autocomplete-suggestions')

    @property
    def input(self):
        return self.browser.find_element_by_class_name('js-search-field')

    def fill_input(self):
        """Enter correct search term."""
        self.wait.until(EC.presence_of_element_located(
            (By.CLASS_NAME, 'js-search-field')
        ))
        send_keys_and_wait(self.input, self.query)

    def test_autocomplete_can_expand_and_collapse(self):
        """
        Test the autocomplete behavior.

        Autocomplete should minimize during user typing correct search query
        Autocomplete should minimize by removing search query.
        """
        # fill input and autocomplete expands
        self.assertTrue(self.autocomplete.is_displayed())

        # remove search term ...
        send_keys_and_wait(self.input, Keys.BACKSPACE * len(self.query))

        # ... and autocomplete collapse
        self.assertFalse(self.autocomplete.is_displayed())

    def test_autocomplete_item_link(self):
        """Every autocomplete item should contain link on page."""
        self.wait.until(EC.presence_of_element_located(
            (By.CLASS_NAME, 'autocomplete-suggestion')
        ))
        self.wait.until(EC.visibility_of_element_located(
            (By.CLASS_NAME, 'autocomplete-suggestion')
        ))
        first_item = self.autocomplete.find_element_by_class_name('autocomplete-suggestion')
        first_item.click()

        self.wait.until(EC.url_contains('/gbi/products/'))
        self.assertTrue('/gbi/products/' in self.browser.current_url)

    def test_autocomplete_see_all_item(self):
        """
        Autocomplete should contain "see all" item.

        "See all" item links on search results page.
        """
        last_item = self.autocomplete.find_element_by_class_name('search-more-link')
        click_and_wait(last_item)

        self.assertTrue('/search/' in self.browser.current_url)

    def test_search_have_results(self):
        """Search results page should contain links on relevant pages."""
        button_submit = self.browser.find_element_by_id('search-btn')
        click_and_wait(button_submit)

        self.assertTrue(self.browser.find_element_by_link_text('Category root #0'))
        self.assertTrue(self.browser.find_element_by_link_text('Category #0 of #1'))

    def test_inactive_product_not_in_search_autocomplete(self):
        test_product = Product.objects.first()
        test_product.page.is_active = False
        test_product.page.save()

        send_keys_and_wait(self.input, test_product.name)

        with self.assertRaises(NoSuchElementException):
            self.browser.find_element_by_link_text(test_product.name)

    def test_search_results_empty(self):
        """Search results for wrong term should contain empty result set."""
        self.input.clear()
        send_keys_and_wait(self.input, 'Not existing search query')
        button_submit = self.browser.find_element_by_id('search-btn')

        click_and_wait(button_submit)
        h1 = self.browser.find_element_by_tag_name('h1')

        self.assertTrue(h1.text == 'По вашему запросу ничего не найдено')


class IndexPage(SeleniumTestCase):
    def setUp(self):
        super(IndexPage, self).setUp()
        self.browser.get(self.live_server_url)

    def fill_and_send_backcall_request_form(self):
        self.browser.execute_script('$("#id_name").val("");')
        self.browser.execute_script('$("#id_phone").val("");')

        name_field = self.browser.find_element_by_id('id_name')
        phone_field = self.browser.find_element_by_id('id_phone')

        send_keys_and_wait(name_field, 'Yo')
        send_keys_and_wait(phone_field, '22222222222')

        send_btn = self.browser.find_element_by_class_name('js-send-backcall')
        send_btn.click()
        wait(3)

    def test_backcall_request(self):
        self.browser.find_element_by_class_name('js-open-modal').click()
        modal = self.browser.find_element_by_class_name('js-modal')
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
