import time

from selenium.webdriver.common.keys import Keys
from seleniumrequests import Chrome  # We use this instead of standard selenium
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webelement import WebElement

from django.test import LiveServerTestCase
from django.core.urlresolvers import reverse

from stroyprombeton.models import Category, Product


def wait(seconds=1):
    """Simple wrapper on time.sleep() method."""
    time.sleep(seconds)


def hover(browser, element):
    """Perform a hover over an element."""
    hover_action = ActionChains(browser).move_to_element(element)
    wait()
    hover_action.perform()


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
        product_page = (self.live_server_url +
                        reverse('product', args=(product_id,)))
        self.browser.get(product_page)
        if quantity:
            q = self.browser.find_element_by_class_name('js-product-count')
            q.clear()
            send_keys_and_wait(q, quantity, waiting_time=waiting_time)
        click_and_wait(self.browser.find_element_by_class_name('js-add-basket'), waiting_time=waiting_time)


class SeleniumTestCase(LiveServerTestCase):
    """Common superclass for running selenium-based tests."""

    @classmethod
    def setUpClass(cls):
        """Instantiate browser instance."""
        super(SeleniumTestCase, cls).setUpClass()
        cls.browser = Chrome()
        cls.browser.implicitly_wait(5)
        cls.browser.maximize_window()

    def prepareFixtures(self):
        root_category = Category.objects.create(
            id=1,
            name='Test Root Category'
        )
        self.child_category = Category.objects.create(
            id=2,
            name='Test Child Category',
            parent=root_category
        )
        self.product1 = Product.objects.create(
            id=1,
            price=1447.21,
            code=350,
            name='Test product one',
            category=self.child_category
        )
        self.product2 = Product.objects.create(
            id=2,
            price=666.21,
            code=24,
            name='Test product two',
            category=self.child_category
        )

    def setUp(self):
        self.prepareFixtures()

    @classmethod
    def tearDownClass(cls):
        """Closes selenium's session."""
        cls.browser.quit()
        super(SeleniumTestCase, cls).tearDownClass()


class HeaderCart(SeleniumTestCase, BuyMixin):

    def setUp(self):
        super(HeaderCart, self).setUp()
        self.browser.get(self.live_server_url)

    def assertCartEmpty(self):
        self.show_cart()
        is_empty = self.browser.find_element_by_class_name(
            'empty-cart-dropdown')
        self.assertTrue(is_empty.is_displayed())
        self.assertIn('Нет выбранных позиций', is_empty.text)

    @property
    def cart(self):
        return self.browser.find_element_by_id('cartInner')

    @property
    def positions(self):
        return self.browser.find_element_by_class_name('basket-content').text

    def show_cart(self):
        hover(self.browser, self.cart)

    def test_empty_dropdown(self):
        self.assertCartEmpty()

    def test_add_to_cart_updates_header(self):
        self.buy(product_id=1)
        self.show_cart()
        self.assertIn('1', self.positions)
        self.assertIn(self.product1.name, self.browser.find_element_by_class_name(
            'mbasket-items').text)

    def test_delete_from_header_cart(self):
        self.buy(product_id=1)
        self.buy(product_id=2)
        self.show_cart()
        click_and_wait(self.browser.find_element_by_xpath(
            '//*[@id="dropdown-basket"]/table/tbody/tr[1]/td[4]/a/i'
        ))
        self.assertIn('1', self.positions)

    def test_flush_cart(self):
        self.buy(product_id=1)
        self.buy(product_id=2)
        self.show_cart()
        click_and_wait(self.browser.find_element_by_class_name('js-reset'))
        self.assertCartEmpty()


class ProductPage(SeleniumTestCase, BuyMixin):

    def test_buy_product(self):
        self.buy()
        self.assertIn('1', self.browser.find_element_by_class_name(
            'basket-content').text)

    def test_buy_two_products(self):
        self.buy()
        self.buy(product_id=2)
        self.assertIn('2', self.browser.find_element_by_class_name(
            'basket-content').text)

    def test_buy_product_with_count(self):
        self.buy(quantity=42)
        hover(
            self.browser,
            self.browser.find_element_by_id('cartInner')
        )
        self.assertIn('42', self.browser.find_element_by_xpath(
            '//*[@id="dropdown-basket"]/table/tbody/tr[1]/td[3]'
        ).text)

    def test_tooltip(self):
        self.buy(waiting_time=0)
        tooltip = self.browser.find_element_by_id('tooltip')
        self.assertTrue(tooltip.is_displayed())


class OrderPage(SeleniumTestCase, BuyMixin):

    def proceed_order_page(self):
        self.browser.get(self.live_server_url +
                         reverse('ecommerce:order_page'))

    def test_order_page_actual_count_of_rows(self):
        self.buy()
        self.buy(product_id=2)
        self.proceed_order_page()
        products_in_table = self.browser.find_elements_by_class_name(
            'js-product-row')
        self.assertEqual(len(products_in_table), 2)

    def test_order_page_remove_row(self):
        self.buy()
        self.buy(product_id=2)
        self.proceed_order_page()
        click_and_wait(self.browser.find_element_by_xpath(
            '/html/body/div[2]/div[2]/div[2]/div/div[2]/div/table/tbody/tr[1]/td[5]/a/i'))
        products_in_table = self.browser.find_elements_by_class_name(
            'js-product-row')
        self.assertEqual(len(products_in_table), 1)

    def test_order_page_remove_all_products(self):
        self.buy()
        self.proceed_order_page()
        click_and_wait(self.browser.find_element_by_xpath(
            '/html/body/div[2]/div[2]/div[2]/div/div[2]/div/table/tbody/tr[1]/td[5]/a/i'))
        self.assertIn('Нет выбранных позиций', self.browser.find_element_by_class_name(
            'js-order-contain').text)

    def test_change_count_in_cart(self):
        self.buy()
        self.proceed_order_page()
        counter = self.browser.find_element_by_class_name('js-prod-count')
        counter.clear()
        send_keys_and_wait(counter, 42)
        click_and_wait(self.browser.find_element_by_class_name(
            'js-order-contain'))  # Hack
        self.assertIn(str(self.product1.price * 42),
                      self.browser.find_element_by_class_name('js-order-total').text)


class CategoryPage(SeleniumTestCase):

    @classmethod
    def setUpClass(cls):
        super(CategoryPage, cls).setUpClass()
        cls.buy_button = 'js-category-buy'
        cls.quantity = 'js-product-count'

    def setUp(self):
        super(CategoryPage, self).setUp()
        self.browser.get(self.live_server_url +
                         reverse('category', args=(self.child_category.id,)))

    def test_buy_product(self):
        click_and_wait(self.browser.find_element_by_xpath(
            '//*[@id="gbi-list"]/table/tbody/tr[2]/td[5]/div/div[2]/span/input'
        ))
        self.assertIn('1', self.browser.find_element_by_class_name(
            'basket-content').text)

    def test_buy_two_product(self):
        click_and_wait(self.browser.find_element_by_xpath(
            '//*[@id="gbi-list"]/table/tbody/tr[2]/td[5]/div/div[2]/span/input'
        ))
        click_and_wait(self.browser.find_element_by_xpath(
            '//*[@id="gbi-list"]/table/tbody/tr[3]/td[5]/div/div[2]/span/input'
        ))
        self.assertIn('2', self.browser.find_element_by_class_name(
            'basket-content').text)

    def test_buy_product_with_quantity(self):
        first_product_count = self.browser.find_element_by_xpath(
            '//*[@id="gbi-list"]/table/tbody/tr[2]/td[5]/div/div[1]/input')
        first_product_count.clear()
        send_keys_and_wait(first_product_count, '42')
        click_and_wait(self.browser.find_element_by_xpath(
            '//*[@id="gbi-list"]/table/tbody/tr[2]/td[5]/div/div[2]/span/input'
        ))
        self.assertIn('1', self.browser.find_element_by_class_name(
            'basket-content').text)
        hover(self.browser, self.browser.find_element_by_id('cartInner'))
        self.assertIn('42', self.browser.find_element_by_class_name(
            'js-header-prod-count').text)

    def test_tooltip(self):
        click_and_wait(self.browser.find_element_by_xpath(
            '//*[@id="gbi-list"]/table/tbody/tr[2]/td[5]/div/div[2]/span/input'
        ))
        tooltip = self.browser.find_element_by_xpath(
            '//*[@id="gbi-list"]/table/tbody/tr[2]/td[5]/div/div[2]/span/span'
        )
        self.assertTrue(tooltip.is_displayed())


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
        return self.browser.find_element_by_class_name(
            'autocomplete-suggestions')

    @property
    def input(self):
        return self.browser.find_element_by_class_name('search-input')

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
        last_item = self.autocomplete.find_element_by_class_name('autocomplete-last-item')

        click_and_wait(last_item)

        self.assertTrue('/search/' in self.browser.current_url)

    def test_search_have_results(self):
        """Search results page should contain links on relevant pages"""
        button_submit = self.browser.find_element_by_id('search-submit')
        click_and_wait(button_submit)

        self.assertTrue(self.browser.find_element_by_link_text('Test Root Category'))
        self.assertTrue(self.browser.find_element_by_link_text('Test Child Category'))

    def test_search_results_empty(self):
        """Search results for wrong term should contain empty result set"""
        send_keys_and_wait(self.input, 'Not existing search query')
        button_submit = self.browser.find_element_by_id('search-submit')

        click_and_wait(button_submit)
        h1 = self.browser.find_element_by_tag_name('h1')

        self.assertTrue(h1.text == 'По вашему запросу ничего не найдено')


class PageAccordion(SeleniumTestCase):

    def setUp(self):
        super(PageAccordion, self).setUp()
        self.browser.get(self.live_server_url)
        self.browser.execute_script('localStorage.clear();')
        self.browser.get(self.live_server_url)
        wait()

    @property
    def accordion_title(self):
        return self.browser.find_element_by_id('cat-1')

    @property
    def accordion_content(self):
        return self.browser.find_element_by_id('content-1')

    def test_accordion_minimized(self):
        """Accordion item should be minimized by default"""
        self.assertFalse(self.accordion_content.is_displayed())

    def test_accordion_expand(self):
        """Accordion item should expand by click on title"""
        accordion_title = self.accordion_title
        accordion_content = self.accordion_content

        click_and_wait(accordion_title)

        self.assertTrue(accordion_content.is_displayed())

    def test_accordion_minimize_by_double_click(self):
        """Accordion item should be minimized by two clicks on title"""
        accordion_title = self.accordion_title
        accordion_content = self.accordion_content

        click_and_wait(accordion_title)
        click_and_wait(accordion_title)

        self.assertFalse(accordion_content.is_displayed())
