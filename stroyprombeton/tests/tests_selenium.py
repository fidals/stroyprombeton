import time

from selenium.webdriver.common.keys import Keys
from seleniumrequests import Chrome  # We use this instead of standard selenium
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webelement import WebElement

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.test import LiveServerTestCase

from stroyprombeton.models import Category


def wait(seconds=1):
    """Simple wrapper on time.sleep() method."""
    time.sleep(seconds)


def hover(browser, element):
    """Perform a hover over an element."""
    hover_action = ActionChains(browser).move_to_element(element)
    hover_action.perform()


class SeleniumTestCase(LiveServerTestCase):
    """Common superclass for running selenium-based tests."""

    fixtures = ['dump.json']

    @classmethod
    def setUpClass(cls):
        """Instantiate browser instance."""
        super(SeleniumTestCase, cls).setUpClass()
        cls.browser = Chrome(settings.CHROMEDRIVER)
        cls.browser.implicitly_wait(5)
        cls.browser.maximize_window()

    @classmethod
    def tearDownClass(cls):
        """Close selenium session."""
        cls.browser.quit()
        super(SeleniumTestCase, cls).tearDownClass()


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


class BuyMixin:
    """Allow to add products to cart."""

    def buy(self, *, product_id=1, quantity=None, waiting_time=1):
        product_page = (self.live_server_url + reverse('product', args=(product_id,)))
        self.browser.get(product_page)
        if quantity:
            q = self.browser.find_element_by_class_name('js-product-count')
            q.clear()
            send_keys_and_wait(q, quantity, waiting_time=waiting_time)
        click_and_wait(self.browser.find_element_by_class_name('js-add-basket'),
                       waiting_time=waiting_time)


class HeaderCart(SeleniumTestCase, BuyMixin):
    def setUp(self):
        super(HeaderCart, self).setUp()
        self.browser.get(self.live_server_url)

    @property
    def cart(self):
        return self.browser.find_element_by_class_name('js-cart-trigger')

    @property
    def positions(self):
        return self.browser.find_element_by_class_name('basket-content').text

    def show_cart(self):
        hover(self.browser, self.cart)

    def test_empty_cart_dropdown(self):
        self.show_cart()
        cart_wrapper = self.browser.find_element_by_class_name('js-cart-trigger')
        cart_wrapper_classes = cart_wrapper.get_attribute('class')

        self.assertNotIn('active', cart_wrapper_classes)

    # TODO: Doesn't work cause new Cart dropdown layout
    # def test_add_to_cart_updates_header(self):
    #     self.buy(product_id=1)
    #     self.show_cart()
    #     self.assertIn('1', self.positions)
    #     self.assertIn(self.product1.name, self.browser.find_element_by_class_name(
    #         'mbasket-items').text)

    # TODO: Doesn't work cause new Cart dropdown layout
    # def test_delete_from_header_cart(self):
    #     self.buy(product_id=1)
    #     self.buy(product_id=2)
    #     self.show_cart()
    #     click_and_wait(self.browser.find_element_by_xpath(
    #         '//*[@id="dropdown-basket"]/table/tbody/tr[1]/td[4]/a/i'
    #     ))
    #     self.assertIn('1', self.positions)

    # TODO: Doesn't work cause new Cart dropdown layout
    # def test_flush_cart(self):
    #     self.buy(product_id=1)
    #     self.buy(product_id=2)
    #     self.show_cart()
    #     click_and_wait(self.browser.find_element_by_class_name('js-reset'))
    #     self.assertCartEmpty()


# class ProductPage(SeleniumTestCase, BuyMixin):
    # TODO: Doesn't work cause new Cart dropdown layout
    # def test_buy_product(self):
    #     self.buy()
    #     self.assertIn('1', self.browser.find_element_by_class_name(
    #         'basket-content').text)

    # TODO: Doesn't work cause new Cart dropdown layout
    # def test_buy_two_products(self):
    #     self.buy()
    #     self.buy(product_id=2)
    #     self.assertIn('2', self.browser.find_element_by_class_name(
    #         'basket-content').text)

    # TODO: Doesn't work cause new Cart dropdown layout
    # def test_buy_product_with_count(self):
    #     self.buy(quantity=42)
    #     hover(
    #         self.browser,
    #         self.browser.find_element_by_id('cartInner')
    #     )
    #     self.assertIn('42', self.browser.find_element_by_xpath(
    #         '//*[@id="dropdown-basket"]/table/tbody/tr[1]/td[3]'
    #     ).text)

    # TODO: Doesn't work cause new Cart dropdown layout
    # def test_tooltip(self):
    #     self.buy(waiting_time=0)
    #     tooltip = self.browser.find_element_by_id('tooltip')
    #     self.assertTrue(tooltip.is_displayed())

# TODO: This tests wouldn't work cause of new HTML
# class OrderPage(SeleniumTestCase, BuyMixin):
#     def proceed_order_page(self):
#         self.browser.get(self.live_server_url + reverse('ecommerce:order_page'))
#
#     def test_order_page_actual_count_of_rows(self):
#         self.buy()
#         self.buy(product_id=2)
#         self.proceed_order_page()
#         products_in_table = self.browser.find_elements_by_class_name('js-product-row')
#         self.assertEqual(len(products_in_table), 2)
#
#     def test_order_page_remove_row(self):
#         self.buy()
#         self.buy(product_id=2)
#         self.proceed_order_page()
#         click_and_wait(self.browser.find_element_by_xpath(
#             '/html/body/div[2]/div[2]/div[2]/div/div[2]/div/table/tbody/tr[1]/td[5]/a/i'))
#         products_in_table = self.browser.find_elements_by_class_name('js-product-row')
#         self.assertEqual(len(products_in_table), 1)
#
#     def test_order_page_remove_all_products(self):
#         self.buy()
#         self.proceed_order_page()
#         click_and_wait(self.browser.find_element_by_xpath(
#             '/html/body/div[2]/div[2]/div[2]/div/div[2]/div/table/tbody/tr[1]/td[5]/a/i'))
#         self.assertIn('Нет выбранных позиций', self.browser.find_element_by_class_name(
#             'js-order-contain').text)
#
#     def test_change_count_in_cart(self):
#         self.buy()
#         self.proceed_order_page()
#         counter = self.browser.find_element_by_class_name('js-prod-count')
#         counter.clear()
#         send_keys_and_wait(counter, 42)
#         click_and_wait(self.browser.find_element_by_class_name(
#             'js-order-contain'))  # Hack
#         self.assertIn(str(self.product1.price * 42),
#                       self.browser.find_element_by_class_name('js-order-total').text)


class CategoryPage(SeleniumTestCase):
    @classmethod
    def setUpClass(cls):
        super(CategoryPage, cls).setUpClass()
        cls.buy_button = 'js-category-buy'
        cls.quantity = 'js-product-count'

    def setUp(self):
        server = self.live_server_url
        self.testing_url = lambda category_id: server + reverse('category', args=(category_id,))

        root_category = Category.objects.filter(parent=None).first()
        children_category = Category.objects.filter(parent=root_category).first()
        category_with_product_less_then_load_limit = Category.objects.annotate(
            prod_count=Count('products')).exclude(prod_count=0).filter(
                prod_count__lt=settings.PRODUCTS_TO_LOAD).first()

        self.root_category = self.testing_url(root_category.id)
        self.children_category = self.testing_url(children_category.id)
        self.deep_children_category = self.testing_url(
            category_with_product_less_then_load_limit.id)

    def click_buy_button(self):
        click_and_wait(self.browser.find_element_by_class_name('js-category-buy'))

    def get_tables_rows_count(self):
        return len(self.browser.find_elements_by_class_name('table-tr'))

    def get_load_more_button(self):
        return self.browser.find_element_by_id('load-more-products')

    def get_load_more_button_classes(self):
        return self.browser.find_element_by_id('load-more-products').get_attribute('class')

    # TODO: Doesn't work cause new Cart dropdown layout
    # def test_buy_product(self):
    #     self.click_buy_button()
    #     self.assertIn('1', self.browser.find_element_by_class_name(
    #         'basket-content').text)

    # TODO: Doesn't work cause new Cart dropdown layout
    # def test_buy_two_product(self):
    #     self.click_buy_button()
    #     self.click_buy_button()
    #     self.assertIn('2', self.browser.find_element_by_class_name(
    #         'basket-content').text)

    # TODO: Doesn't work cause new Cart dropdown layout
    # def test_buy_product_with_quantity(self):
    #     first_product_count = self.browser.find_element_by_class_name('js-count-input')
    #     first_product_count.clear()
    #     send_keys_and_wait(first_product_count, '42')
    #     self.click_buy_button()

    #     self.assertIn('1', self.browser.find_element_by_class_name(
    #         'basket-content').text)
    #     hover(self.browser, self.browser.find_element_by_id('cartInner'))
    #     self.assertIn('42', self.browser.find_element_by_class_name(
    #         'js-header-prod-count').text)

    def test_tooltip(self):
        """We should see tooltip after clicking on `Заказать` button."""

        self.browser.get(self.root_category)
        click_and_wait(self.browser.find_element_by_class_name('js-category-buy'))
        tooltip = self.browser.find_element_by_class_name('js-popover')
        self.assertTrue(tooltip.is_displayed())

    def test_load_more_products(self):
        """We able to load more products by clicking on `Показать ещё` link."""

        self.browser.get(self.root_category)
        before_load_products = self.get_tables_rows_count()
        click_and_wait(self.get_load_more_button())
        after_load_products = self.get_tables_rows_count()

        self.assertTrue(before_load_products < after_load_products)

    def test_load_more_button_disabled_state_with_few_products(self):
        """
        `Показать ещё` link should be disabled by default if there are less
        than settings.PRODUCTS_TO_LOAD products on page.
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

        self.browser.get(self.root_category)
        filter_field = self.browser.find_element_by_id('search-filter')
        before_filter_products = self.get_tables_rows_count()
        send_keys_and_wait(filter_field, '#10')
        after_filter_products = self.get_tables_rows_count()

        self.assertTrue(before_filter_products > after_filter_products)

    def test_filter_products_and_disabled_state(self):
        """
        If we filter products and load more products several times - we should
        see that `Показать ещё` link becomes disabled. That means that there are
        no more filtered products to load from server.
        """

        self.browser.get(self.root_category)
        filter_field = self.browser.find_element_by_id('search-filter')
        send_keys_and_wait(filter_field, '#10')

        load_more_button = self.get_load_more_button()
        click_and_wait(load_more_button)
        click_and_wait(load_more_button)

        self.assertIn('disabled', self.get_load_more_button_classes())


class Search(SeleniumTestCase):
    """Selenium-based tests for Search"""

    def setUp(self):
        super(Search, self).setUp()
        self.browser.get(self.live_server_url)
        wait()
        self.query = 'Test'
        self.fill_input()

    @property
    def autocomplete(self):
        return self.browser.find_element_by_class_name('autocomplete-suggestions')

    @property
    def input(self):
        return self.browser.find_element_by_class_name('js-search-field')

    def fill_input(self):
        """Enter correct search term"""

        send_keys_and_wait(self.input, self.query)

    def test_autocomplete_can_expand_and_collapse(self):
        """
        Autocomplete should minimize during user typing correct search query
        Autocomplete should minimize by removing search query
        """

        # fill input and autocomplete expands
        self.assertTrue(self.autocomplete.is_displayed())

        # remove search term ...
        send_keys_and_wait(self.input, Keys.BACKSPACE * len(self.query))

        # ... and autocomplete collapse
        self.assertFalse(self.autocomplete.is_displayed())

    def test_autocomplete_item_link(self):
        """First autocomplete item should link on category page by click"""

        first_item = self.autocomplete.find_element_by_css_selector(':first-child')
        click_and_wait(first_item)

        self.assertTrue('/gbi/categories/' in self.browser.current_url)

    def test_autocomplete_see_all_item(self):
        """
        Autocomplete should contain "see all" item.
        "See all" item links on search results page
        """
        last_item = self.autocomplete.find_element_by_class_name('search-more-link')
        click_and_wait(last_item)

        self.assertTrue('/search/' in self.browser.current_url)

    def test_search_have_results(self):
        """Search results page should contain links on relevant pages"""
        button_submit = self.browser.find_element_by_class_name('search-btn')
        click_and_wait(button_submit)

        self.assertTrue(self.browser.find_element_by_link_text('Test Root Category'))
        self.assertTrue(self.browser.find_element_by_link_text('Test Child Category'))

    def test_search_results_empty(self):
        """Search results for wrong term should contain empty result set"""
        send_keys_and_wait(self.input, 'Not existing search query')
        button_submit = self.browser.find_element_by_class_name('search-btn')

        click_and_wait(button_submit)
        h1 = self.browser.find_element_by_tag_name('h1')

        self.assertTrue(h1.text == 'По вашему запросу ничего не найдено')
