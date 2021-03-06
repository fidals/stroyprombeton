import time

from django.conf import settings
from django.test import override_settings, LiveServerTestCase, TestCase
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebDriverException
from seleniumrequests import Remote

from catalog.helpers import reverse_catalog_url
from stroyprombeton import models as stb_models

disable_celery = override_settings(USE_CELERY=False)


def wait(seconds=1):
    """Simple wrapper on time.sleep() method."""
    time.sleep(seconds)


CAPABILITIES = {
    'browserName': 'chrome',
    'chromeOptions': {
        # the rationale for these options: https://bit.ly/2Vo6klZ
        'args': [
            'start-maximized',
            'enable-automation',
            '--disable-infobars',
            '--no-sandbox',
            '--disable-browser-side-navigation',
        ]
    }
}


class BaseSeleniumTestCase(LiveServerTestCase):
    """Common superclass for running selenium-based tests."""

    host = settings.LIVESERVER_HOST

    @classmethod
    def setUpClass(cls):
        """Instantiate browser instance."""
        super().setUpClass()

        cls.browser = Remote(
            command_executor=settings.SELENIUM_URL,
            desired_capabilities=CAPABILITIES,
        )
        cls.wait = WebDriverWait(cls.browser, settings.SELENIUM_WAIT_SECONDS)
        cls.browser.implicitly_wait(settings.SELENIUM_WAIT_SECONDS)
        cls.browser.set_page_load_timeout(settings.SELENIUM_TIMEOUT_SECONDS)
        time.sleep(1.0)
        try:
            cls.browser.maximize_window()
        except WebDriverException:
            print('Failed to maximize window')  # Ignore CPDBear

    @classmethod
    def tearDownClass(cls):
        """Close selenium session."""
        cls.browser.quit()
        super().tearDownClass()

    def click(self, click_locator):
        self.wait.until(EC.element_to_be_clickable(
            click_locator
        )).click()

    def click_and_wait(self, click_locator, wait_condition):
        self.click(click_locator)
        self.wait.until(wait_condition)

    def send_keys_and_wait(self, keys, locator, expected_keys=''):
        el = self.wait.until(EC.visibility_of_element_located(locator))
        el.clear()
        str_keys = str(keys)
        el.send_keys(str_keys)
        self.wait.until(EC.text_to_be_present_in_element_value(locator, expected_keys or str_keys))


class CategoryTestMixin:

    category: stb_models.Category = NotImplemented

    def get_category_path(
        self,
        category: stb_models.Category=None,
        route_name='category',
        tags: stb_models.TagQuerySet=None,
        sorting: int=None,
        query_string: dict=None,
    ):
        category = category or self.category
        route_kwargs = {'category_id': category.id}
        return reverse_catalog_url(
            route_name, route_kwargs, tags, sorting, query_string
        )
