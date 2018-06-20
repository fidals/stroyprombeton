import time

from django.conf import settings
from django.test import override_settings, LiveServerTestCase
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from seleniumrequests import Remote

disable_celery = override_settings(USE_CELERY=False)


def wait(seconds=1):
    """Simple wrapper on time.sleep() method."""
    time.sleep(seconds)


class BaseSeleniumTestCase(LiveServerTestCase):
    """Common superclass for running selenium-based tests."""

    @classmethod
    def setUpClass(cls):
        """Instantiate browser instance."""
        super().setUpClass()
        cls.browser = Remote(
            command_executor=settings.SELENIUM_URL,
            desired_capabilities=DesiredCapabilities.CHROME
        )
        cls.wait = WebDriverWait(cls.browser, 60)
        cls.browser.implicitly_wait(30)
        cls.browser.set_page_load_timeout(30)
        # Fresh created browser failures on maximizing window.
        # This bug is won't fixed by selenium guys https://goo.gl/6Ttguf
        # Ohh, so selenium is so selenium ...
        # UPD 19.05.18: Seems it works, so we enable it to reduce number of errors
        time.sleep(1.0)
        cls.browser.maximize_window()

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
