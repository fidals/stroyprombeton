from selenium import webdriver

from django.core.urlresolvers import reverse
from django.test import LiveServerTestCase

from stroyprombeton.models import Product
from stroyprombeton.tests.helpers import wait


class SeleniumTestCase(LiveServerTestCase):
    """Common superclass for running selenium-based tests."""

    fixtures = ['dump.json']

    @classmethod
    def setUpClass(cls):
        """Instantiate browser instance."""
        super(SeleniumTestCase, cls).setUpClass()
        mobile_emulation = {'deviceName': 'Apple iPhone 5'}
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option('mobileEmulation', mobile_emulation)
        cls.browser = webdriver.Chrome(chrome_options=chrome_options)
        cls.browser.implicitly_wait(5)
        cls.browser.maximize_window()

    @classmethod
    def tearDownClass(cls):
        """Close selenium session."""
        cls.browser.quit()
        super(SeleniumTestCase, cls).tearDownClass()


class Mobile(SeleniumTestCase):

    def setUp(self):
        """Set up testing urls and dispatch selenium webdriver."""
        self.browser.get(self.live_server_url)
        self.toggler = 'js-mobile-menu-toggler'

    def test_cart(self):
        """Cart should updated after Product buy."""
        product_id = Product.objects.first().id
        product_page = self.live_server_url + reverse('product', args=(product_id,))
        self.browser.get(product_page)

        offer_section = self.browser.find_element_by_class_name('product-order')
        self.browser.execute_script('return arguments[0].scrollIntoView();', offer_section)
        self.browser.find_element_by_id('buy-product').click()
        wait(2)
        size = self.browser.find_element_by_class_name('js-cart-size').text
        price = self.browser.find_element_by_class_name('js-mobile-cart-price').text

        self.assertTrue(int(size) > 0)
        self.assertTrue(int(price) > 0)
