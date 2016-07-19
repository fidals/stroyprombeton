import time

from seleniumrequests import Chrome  # We use this instead of standard selenium
from selenium.webdriver.common.action_chains import ActionChains

from django.test import LiveServerTestCase
from django.core.urlresolvers import reverse

from stroyprombeton.models import Category, Product


def wait(seconds=1):
    """Simple wrapper on time.sleep() method."""
    time.sleep(seconds)


def hover(browser, element):
    """Perform a hover over an element."""
    hover_action = ActionChains(browser).move_to_element(element)
    hover_action.perform()


class BuyMixin:
    """Allow to add products to cart."""

    def buy(self, *, product_id=1, quantity=None):
        product_page = (self.live_server_url +
                        reverse('product', args=(product_id,)))
        self.browser.get(product_page)
        if quantity:
            q = self.browser.find_element_by_class_name('js-product-count')
            q.clear()
            q.send_keys(quantity)
        self.browser.find_element_by_class_name('js-add-basket').click()
        wait()


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
            name='Test Child Category'
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
        self.browser.find_element_by_xpath(
            '//*[@id="dropdown-basket"]/table/tbody/tr[1]/td[4]/a/i'
        ).click()
        wait()
        self.assertIn('1', self.positions)

    def test_flush_cart(self):
        self.buy(product_id=1)
        self.buy(product_id=2)
        self.show_cart()
        self.browser.find_element_by_class_name('js-reset').click()
        wait()
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
        self.browser.find_element_by_xpath(
            '/html/body/div[2]/div[2]/div[2]/div/div[2]/div/table/tbody/tr[1]/td[5]/a/i').click()
        wait()
        products_in_table = self.browser.find_elements_by_class_name(
            'js-product-row')
        self.assertEqual(len(products_in_table), 1)

    def test_order_page_remove_all_products(self):
        self.buy()
        self.proceed_order_page()
        self.browser.find_element_by_xpath(
            '/html/body/div[2]/div[2]/div[2]/div/div[2]/div/table/tbody/tr[1]/td[5]/a/i').click()
        wait()
        self.assertIn('Нет выбранных позиций', self.browser.find_element_by_class_name(
            'js-order-contain').text)

    def test_change_count_in_cart(self):
        self.buy()
        self.proceed_order_page()
        counter = self.browser.find_element_by_class_name('js-prod-count')
        counter.clear()
        counter.send_keys(42)
        self.browser.find_element_by_class_name(
            'js-order-contain').click()  # Hack
        wait()
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
        self.browser.find_element_by_xpath(
            '//*[@id="gbi-list"]/table/tbody/tr[2]/td[5]/div/div[2]/input'
        ).click()
        wait()
        self.assertIn('1', self.browser.find_element_by_class_name(
            'basket-content').text)

    def test_buy_two_product(self):
        self.browser.find_element_by_xpath(
            '//*[@id="gbi-list"]/table/tbody/tr[2]/td[5]/div/div[2]/input'
        ).click()
        wait()
        self.browser.find_element_by_xpath(
            '//*[@id="gbi-list"]/table/tbody/tr[3]/td[5]/div/div[2]/input'
        ).click()
        wait()
        self.assertIn('2', self.browser.find_element_by_class_name(
            'basket-content').text)

    def test_buy_product_with_quantity(self):
        first_product_count = self.browser.find_element_by_xpath(
            '//*[@id="gbi-list"]/table/tbody/tr[2]/td[5]/div/div[1]/input')
        first_product_count.clear()
        first_product_count.send_keys('42')
        self.browser.find_element_by_xpath(
            '//*[@id="gbi-list"]/table/tbody/tr[2]/td[5]/div/div[2]/input'
        ).click()
        wait()
        self.assertIn('1', self.browser.find_element_by_class_name(
            'basket-content').text)
        hover(self.browser, self.browser.find_element_by_id('cartInner'))
        self.assertIn('42', self.browser.find_element_by_class_name(
            'js-header-prod-count').text)
