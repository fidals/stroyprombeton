import time

from selenium.webdriver.common.action_chains import ActionChains
from seleniumrequests import Chrome  # We use this instead of standard selenium

from django.test import LiveServerTestCase
from django.core.urlresolvers import reverse
from django.conf import settings


def wait(seconds=1):
    """Simple wrapper on time.sleep() method."""
    time.sleep(seconds)


def hover(browser, element):
    """Perform a hover over an element."""
    ActionChains(browser).move_to_element(element).perform()


def context_click(browser, element):
    ActionChains(browser).context_click(element).perform()
    wait()


class SeleniumTestCase(LiveServerTestCase):
    """Common superclass for running selenium-based tests."""

    fixtures = ['dump.json', 'admin.json']

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


class AdminPage(SeleniumTestCase):
    """Selenium-based tests for Admin page UI."""

    fixtures = ['dump.json', 'admin.json']

    @classmethod
    def setUpClass(cls):
        super(AdminPage, cls).setUpClass()
        cls.admin_page = cls.live_server_url + reverse('stb_admin:index')
        cls.change_products_url = cls.live_server_url + reverse(
            'stb_admin:stroyprombeton_productpage_changelist')
        cls.login = 'admin'
        cls.password = 'asdfjkl;'
        cls.title_text = 'Stroyprombeton administration'
        cls.product_table = 'paginator'
        cls.active_products = '//*[@id="changelist-filter"]/ul[1]/li[2]/a'
        cls.inactive_products = '//*[@id="changelist-filter"]/ul[1]/li[3]/a'
        cls.price_filter = '//*[@id="changelist-filter"]/ul[2]/li[3]/a'
        cls.filter_by_has_content = '//*[@id="changelist-filter"]/ul[3]/li[2]/a'
        cls.filter_by_has_not_content = '//*[@id="changelist-filter"]/ul[3]/li[3]/a'
        cls.filter_by_has_image = '//*[@id="changelist-filter"]/ul[4]/li[2]/a'
        cls.filter_by_has_not_image = '//*[@id="changelist-filter"]/ul[4]/li[3]/a'
        cls.is_active_img = 'field-is_active'

    def setUp(self):
        """Set up testing url and dispatch selenium webdriver."""
        self.browser.get(self.admin_page)
        login_field = self.browser.find_element_by_id('id_username')
        login_field.clear()
        login_field.send_keys(self.login)
        password_field = self.browser.find_element_by_id('id_password')
        password_field.clear()
        password_field.send_keys(self.password)
        login_form = self.browser.find_element_by_id('login-form')
        login_form.submit()
        wait()

    def get_table_with_products(self):
        return self.browser.find_element_by_class_name(self.product_table)

    def test_login(self):
        """We are able to login to Admin page."""

        admin_title = self.browser.find_element_by_id('site-name')
        self.assertIn(self.title_text, admin_title.text)

    def test_product_price_filter(self):
        """
        Price filter is able to filter products by set range.
        In this case we filter products with 1000 - 2000 price range.
        """
        # separated var for debugging
        self.browser.get(self.change_products_url)
        self.browser.find_element_by_xpath(self.price_filter).click()
        wait()
        product = self.browser.find_element_by_xpath('//*[@id="result_list"]/tbody/tr[1]/td[4]')
        product_price = int(float(product.text))

        self.assertTrue(product_price >= 1000)

    def test_image_filter(self):
        """
        Image filter is able to filter pages by the presence of the image.
        """
        self.browser.get(self.change_products_url)
        self.browser.find_element_by_xpath(self.filter_by_has_image).click()
        wait()

        table = self.get_table_with_products().text

        self.assertTrue('0' in table)

        self.browser.find_element_by_xpath(self.filter_by_has_not_image).click()
        wait()

        table = self.get_table_with_products().text

        self.assertTrue('300' in table)

    def test_content_filter(self):
        """
        Content filter is able to filter pages by the presence of the content.
        """
        self.browser.get(self.change_products_url)
        self.browser.find_element_by_xpath(self.filter_by_has_content).click()
        wait()

        table = self.browser.find_element_by_class_name(self.product_table).text

        self.assertTrue('0' in table)

        self.browser.find_element_by_xpath(self.filter_by_has_not_content).click()
        wait()

        table = self.get_table_with_products().text

        self.assertTrue('300' in table)

    def test_is_active_filter(self):
        """Activity filter returns only active or non active items."""

        self.browser.get(self.change_products_url)
        wait()
        self.browser.find_element_by_xpath(self.active_products).click()
        wait()

        first_product = self.browser.find_element_by_class_name(
            self.is_active_img).find_element_by_tag_name('img')
        first_product_state = first_product.get_attribute('alt')

        self.assertTrue(first_product_state == 'true')

        self.browser.find_element_by_xpath(self.inactive_products).click()
        wait()
        results = self.browser.find_element_by_class_name('paginator')

        self.assertTrue('0' in results.text)
