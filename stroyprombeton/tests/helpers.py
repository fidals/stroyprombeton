import time

from django.conf import settings
from django.test import override_settings, LiveServerTestCase
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from seleniumrequests import Remote

from stroyprombeton.models import Tag, TagGroup

disable_celery = override_settings(USE_CELERY=False)


def wait(seconds=1):
    """Simple wrapper on time.sleep() method."""
    time.sleep(seconds)


def create_doubled_tag(tag_from: Tag=None):
    tag_from = tag_from or Tag.objects.first()
    group_to = TagGroup.objects.exclude(id=tag_from.group.id).first()
    tag_to = Tag.objects.create(
        group=group_to, name=tag_from.name, position=tag_from.position
    )
    tag_to.products.set(tag_from.products.all())
    tag_to.save()
    return tag_to


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
        cls.wait = WebDriverWait(cls.browser, settings.SELENIUM_WAIT_SECONDS)
        cls.browser.implicitly_wait(settings.SELENIUM_WAIT_SECONDS)
        cls.browser.set_page_load_timeout(settings.SELENIUM_TIMEOUT_SECONDS)
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
