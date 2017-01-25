import time

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from seleniumrequests import Chrome  # We use this instead of standard selenium

from django.test import LiveServerTestCase
from django.core.urlresolvers import reverse
from django.conf import settings

from stroyprombeton.models import Product, Category


class HelpersMixin:

    @staticmethod
    def wait(seconds=1):
        """Simple wrapper on time.sleep() method."""
        time.sleep(seconds)

    def hover(self, element):
        """Perform a hover over an element."""
        ActionChains(self.browser).move_to_element(element).perform()

    def context_click(self, element):
        ActionChains(self.browser).context_click(element).perform()
        self.wait()


class AdminMixin:

    admin_urlconf = 'admin:index'
    login = 'admin'
    password = 'asdfjkl;'

    def sign_in(self):
        self.browser.get(self.live_server_url + reverse(self.admin_urlconf))
        login_field = self.browser.find_element_by_id('id_username')
        login_field.clear()
        login_field.send_keys(self.login)
        password_field = self.browser.find_element_by_id('id_password')
        password_field.clear()
        password_field.send_keys(self.password)
        login_form = self.browser.find_element_by_id('login-form')
        login_form.submit()
        HelpersMixin.wait()


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


class AdminPage(SeleniumTestCase, HelpersMixin, AdminMixin):
    """Selenium-based tests for Admin page UI."""

    title_text = 'Stroyprombeton administration'
    product_table = 'paginator'
    active_products = '//*[@id="changelist-filter"]/ul[1]/li[2]/a'
    inactive_products = '//*[@id="changelist-filter"]/ul[1]/li[3]/a'
    price_filter = '//*[@id="changelist-filter"]/ul[2]/li[3]/a'
    filter_by_has_content = '//*[@id="changelist-filter"]/ul[3]/li[2]/a'
    filter_by_has_not_content = '//*[@id="changelist-filter"]/ul[3]/li[3]/a'
    filter_by_has_image = '//*[@id="changelist-filter"]/ul[4]/li[2]/a'
    filter_by_has_not_image = '//*[@id="changelist-filter"]/ul[4]/li[3]/a'
    is_active_img = 'field-is_active'
    autocomplete_text = 'Prod'

    @classmethod
    def setUpClass(cls):
        super(AdminPage, cls).setUpClass()
        cls.change_products_url = cls.live_server_url + reverse(
            'admin:stroyprombeton_productpage_changelist')

    def setUp(self):
        """Set up testing url and dispatch selenium webdriver."""
        self.root_category_id = str(Category.objects.filter(parent=None).first().id)
        self.children_category_id = str(Category.objects.filter(
            parent_id=self.root_category_id).first().id)
        self.deep_children_category_id = str(Category.objects.filter(
            parent_id=self.children_category_id).first().id)
        self.tree_product_id = str(Product.objects.filter(
            category_id=self.deep_children_category_id).first().id)

        self.sign_in()

    @property
    def first_h1(self):
        return self.browser.find_elements_by_tag_name('h1')[1].text

    def get_table_with_products(self):
        return self.browser.find_element_by_class_name(self.product_table)

    def open_js_tree_nodes(self):
        def get_change_state_button(id):
            return self.browser.find_element_by_id(id).find_element_by_tag_name('i')

        def change_state_by_id(id):
            get_change_state_button(id).click()
            self.wait()

        def is_node_open(id):
            return self.browser.find_element_by_id(
                id).find_elements_by_class_name('jstree-children')

        def open_node(*args):
            for id in args:
                if not is_node_open(id):
                    # open node
                    change_state_by_id(id=id)

        def open_sidebar():
            """Sidebar should be opened before the tests."""
            if self.browser.find_elements_by_class_name('collapsed'):
                self.browser.find_element_by_class_name('js-toggle-sidebar').click()
                self.wait()

        open_sidebar()
        open_node(
            self.root_category_id,
            self.children_category_id,
            self.deep_children_category_id
        )

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
        self.wait()
        product = self.browser.find_element_by_xpath('//*[@id="result_list"]/tbody/tr[1]/td[4]')
        product_price = int(float(product.text))

        self.assertTrue(product_price >= 1000)

    def test_image_filter(self):
        """
        Image filter is able to filter pages by the presence of the image.
        """
        self.browser.get(self.change_products_url)
        self.browser.find_element_by_xpath(self.filter_by_has_image).click()
        self.wait()

        table = self.get_table_with_products().text

        self.assertTrue('0' in table)

        self.browser.find_element_by_xpath(self.filter_by_has_not_image).click()
        self.wait()

        table = self.get_table_with_products().text

        self.assertTrue('300' in table)

    def test_content_filter(self):
        """
        Content filter is able to filter pages by the presence of the content.
        """
        self.browser.get(self.change_products_url)
        self.browser.find_element_by_xpath(self.filter_by_has_content).click()
        self.wait()

        table = self.browser.find_element_by_class_name(self.product_table).text

        self.assertTrue('0' in table)

        self.browser.find_element_by_xpath(self.filter_by_has_not_content).click()
        self.wait()

        table = self.get_table_with_products().text

        self.assertTrue('300' in table)

    def test_is_active_filter(self):
        """Activity filter returns only active or non active items."""
        self.browser.get(self.change_products_url)
        self.wait()
        self.browser.find_element_by_xpath(self.active_products).click()
        self.wait()

        first_product = self.browser.find_element_by_class_name(
            self.is_active_img).find_element_by_tag_name('img')
        first_product_state = first_product.get_attribute('alt')

        self.assertTrue(first_product_state == 'true')

        self.browser.find_element_by_xpath(self.inactive_products).click()
        self.wait()
        results = self.browser.find_element_by_class_name('paginator')

        self.assertTrue('0' in results.text)

    def test_search_autocomplete(self):
        """Search should autocomplete queries."""
        self.browser.get(self.change_products_url)
        self.browser.find_element_by_id('searchbar').send_keys(self.autocomplete_text)
        self.wait()

        first_suggested_item = self.browser.find_element_by_class_name(
            'autocomplete-suggestion')
        first_suggested_item_text = first_suggested_item.get_attribute(
            'data-val')

        self.assertTrue(self.autocomplete_text in first_suggested_item_text)

    def test_sidebar_not_on_dashboard(self):
        """Sidebar should be not only on dashboard page."""

        self.browser.get(self.change_products_url)
        sidebar = self.browser.find_element_by_class_name('sidebar')

        self.assertTrue(sidebar.is_displayed())

    def test_tree_fetch_data(self):
        self.open_js_tree_nodes()
        node_children = (self.browser.find_element_by_id(self.deep_children_category_id)
                         .find_elements_by_class_name('jstree-leaf'))
        self.assertGreater(len(node_children), 10)

    def test_tree_redirect_to_entity_edit_page(self):
        """Test redirect to edit entity page by click on jstree's item."""
        self.open_js_tree_nodes()
        expected_h1 = ['Change category page', 'Изменить category page']

        # click at tree's item should redirect us to entity edit page
        root_node = self.browser.find_element_by_id(self.root_category_id)
        root_node.find_element_by_tag_name('a').click()
        self.wait()
        test_h1 = self.first_h1

        self.assertIn(test_h1, expected_h1)

    def test_tree_redirect_to_table_editor_page(self):
        """Click on tree's context menu item should redirect us on table editor page."""
        self.open_js_tree_nodes()
        tree_item = self.browser.find_element_by_id(
            self.tree_product_id).find_element_by_tag_name('a')
        self.context_click(tree_item)
        self.browser.find_elements_by_class_name('vakata-contextmenu-sep')[0].click()
        self.wait()

        test_h1 = self.first_h1
        self.assertEqual(test_h1, 'Table editor')

        test_search_value = self.browser.find_element_by_id('search-field').get_attribute('value')
        self.assertTrue(test_search_value)

    # TODO. This test shouldn't work because of new tab opening.
    # def test_tree_redirect_to_entity_site_page(self):
    #     """Click at tree's context menu item should redirect us to entity's site page."""
        # self.open_js_tree_nodes()
        # tree_item = (self.browser.find_element_by_id(self.root_category_id)
        #              .find_element_by_tag_name('a'))
        # category_h1 = Category.objects.get(id=self.root_category_id).page.h1
        #
        # # open context menu and click at redirect to site's page
        # self.context_click(tree_item)
        # self.browser.find_elements_by_class_name('vakata-contextmenu-sep')[1].click()
        # self.wait()
        # test_h1 = self.browser.find_element_by_tag_name('h1').text
        #
        # self.assertEqual(test_h1, category_h1)

    def test_sidebar_toggle(self):
        """Sidebar should store collapsed state."""
        self.browser.find_element_by_class_name('js-toggle-sidebar').click()
        self.wait()
        body_classes = self.browser.find_element_by_tag_name('body').get_attribute('class')

        self.assertTrue('collapsed' in body_classes)

        self.browser.refresh()
        self.wait()
        body_classes = self.browser.find_element_by_tag_name('body').get_attribute('class')

        self.assertTrue('collapsed' in body_classes)


class TableEditor(SeleniumTestCase, AdminMixin, HelpersMixin):
    """Selenium-based tests for Table Editor [TE]."""

    new_product_name = 'Product'
    autocomplete_text = 'Prod'

    def setUp(self):
        """Set up testing url and dispatch selenium webdriver."""
        self.sign_in()
        self.browser.find_element_by_id('admin-editor-link').click()
        self.wait()

    def refresh_table_editor_page(self):
        self.browser.find_element_by_id('admin-editor-link').click()
        self.wait()

    def trigger_autocomplete(self, selector):
        """Programmatically trigger jQ autocomplete widget."""
        self.browser.execute_script(
            '$("' + selector + '").autocomplete("search");'
        )

    def update_input_value(self, index, new_data):
        """Clear input, pass new data and emulate Return keypress."""
        editable_input = self.browser.find_elements_by_class_name('inline-edit-cell')[index]
        editable_input.clear()
        editable_input.send_keys(str(new_data) + Keys.ENTER)
        self.wait()

    def get_cell(self, index=0):
        """Return WebElement for subsequent manipulations by index."""
        table = self.browser.find_element_by_class_name('jqgrow')
        return table.find_elements_by_tag_name('td')[index]

    def get_current_price(self, index):
        """Return sliced integer price of first product by cell index."""
        raw_string = self.get_cell(index).text

        return int(''.join(raw_string.split(' '))[1:-3])

    def perform_checkbox_toggle(self, checkbox_name):
        """Change checkbox state by checkbox_name."""
        self.get_cell().click()
        checkbox = self.browser.find_element_by_name(checkbox_name)
        old_active_state = checkbox.is_selected()
        checkbox.click()
        checkbox.send_keys(Keys.ENTER)
        self.refresh_table_editor_page()

        self.get_cell().click()
        new_active_state = self.browser.find_element_by_name(checkbox_name).is_selected()

        return old_active_state, new_active_state

    def open_filters(self):
        """Open TE filters cause they are collapsed by default."""
        filters_wrapper = self.browser.find_element_by_class_name('js-filter-wrapper')

        if not filters_wrapper.is_displayed():
            self.browser.find_element_by_class_name('js-hide-filter').click()
            self.wait()

    def check_filters_and_table_headers_equality(self):
        """TE filters and table headers text should be equal."""
        filters = self.browser.find_elements_by_class_name('js-sortable-item')

        for index, item in enumerate(filters):
            filter_text = item.text.lower()
            table_header_text = self.browser.find_elements_by_class_name('ui-th-div')[index + 1].text.lower()

            self.assertIn(table_header_text, filter_text)

    def add_col_to_grid(self, col_name):
        filter_fields = self.browser.find_elements_by_class_name('filter-fields-label')

        def is_correct_col(col):
            return col_name in col.get_attribute('for')

        next(filter(is_correct_col, filter_fields)).click()
        self.save_filters()

    def save_filters(self):
        self.browser.find_element_by_class_name('js-save-filters').click()
        self.wait(2)

    def test_products_loaded(self):
        """TE should have all products."""
        rows = self.browser.find_elements_by_class_name('jqgrow')

        self.assertTrue(len(rows) > 0)

    def test_edit_product_name(self):
        """We could change Product name from TE."""
        self.get_cell(1).click()
        self.update_input_value(0, self.new_product_name)
        self.refresh_table_editor_page()
        updated_name = self.get_cell(1).text

        self.assertEqual(updated_name, self.new_product_name)

    def test_edit_product_price(self):
        """We could change Product price from TE."""
        price_cell_index = 2
        price_cell_input = 1
        new_price = self.get_current_price(price_cell_index) + 100
        self.get_cell(price_cell_index).click()
        self.wait()
        self.update_input_value(price_cell_input, new_price)
        self.refresh_table_editor_page()
        updated_price = self.get_current_price(price_cell_index)

        self.assertEqual(updated_price, new_price)

    def test_edit_product_activity(self):
        """We could change Product is_active state from TE."""
        self.open_filters()
        self.add_col_to_grid('is_active')
        old_active_state, new_active_state = self.perform_checkbox_toggle('page_is_active')

        self.assertNotEqual(new_active_state, old_active_state)

    def test_edit_product_popularity(self):
        """We could change Product price is_popular state from TE."""
        self.open_filters()
        self.add_col_to_grid('is_popular')
        old_popular_state, new_popular_state = self.perform_checkbox_toggle('is_popular')

        self.assertNotEqual(new_popular_state, old_popular_state)

    def test_remove_product(self):
        """We could remove Product from TE."""
        old_first_row_id = self.get_cell().text
        self.browser.find_element_by_class_name('js-confirm-delete-modal').click()
        self.wait()
        self.browser.find_element_by_class_name('js-modal-delete').click()
        self.wait()
        new_first_row_id = self.get_cell().text

        self.assertNotEqual(old_first_row_id, new_first_row_id)

    def test_sort_table_by_id(self):
        first_product_id_before = self.get_cell().text
        self.browser.find_element_by_class_name('ui-jqgrid-sortable').click()
        self.browser.find_element_by_class_name('ui-jqgrid-sortable').click()
        first_product_id_after = self.get_cell().text

        self.assertNotEqual(first_product_id_before, first_product_id_after)

    def test_sort_table_by_price(self):
        first_product_price_before = self.get_cell(1).text
        name_header = self.browser.find_elements_by_class_name('ui-jqgrid-sortable')[1]
        name_header.click()
        name_header.click()
        first_product_price_after = self.get_cell(1).text

        self.assertNotEqual(first_product_price_before, first_product_price_after)

    def test_filter_table(self):
        """We could make live search in TE."""
        rows_before = len(self.browser.find_elements_by_class_name('jqgrow'))
        search_field = self.browser.find_element_by_id('search-field')
        search_field.send_keys('384')
        self.wait(2)
        rows_after = len(self.browser.find_elements_by_class_name('jqgrow'))

        self.assertNotEqual(rows_before, rows_after)

    def test_filters_equals_table_headers(self):
        """Headers in TE should be equal to chosen filters respectively."""
        self.open_filters()
        self.check_filters_and_table_headers_equality()

    def test_save_and_drop_custom_filters(self):
        """
        Headers in TE should be generated based on user settings in localStorage.

        This test case is contains save & drop cases cause they are depends on each other.
        """
        self.browser.refresh()
        self.open_filters()

        checkboxes = self.browser.find_elements_by_class_name('filter-fields-item')

        for index, item in enumerate(checkboxes):
            self.browser.find_elements_by_class_name('filter-fields-item')[index].click()

        self.save_filters()
        self.check_filters_and_table_headers_equality()

        self.browser.refresh()
        self.open_filters()
        self.wait(2)

        self.browser.find_element_by_class_name('js-drop-filters').click()
        self.wait(2)
        self.check_filters_and_table_headers_equality()

    def test_non_existing_category_change(self):
        """We should see popover after trying to change Product's category to non existing one."""
        self.get_cell().click()
        self.update_input_value(3, 'yo')

        popover = self.browser.find_element_by_class_name('webui-popover')

        self.assertTrue(popover.is_displayed())

    def test_new_entity_creation(self):
        new_entity_text = 'A New stuff'

        # Trigger entity creation modal & input data:
        self.browser.find_element_by_css_selector('button[data-target="#add-entity"]').click()
        self.browser.find_element_by_id('entity-name').send_keys(new_entity_text)
        self.browser.find_element_by_id('entity-price').send_keys(123)

        # Check is autocomplete works for category search by manual triggering it:
        self.browser.find_element_by_id('entity-category').send_keys('Category #0')
        self.wait()
        self.trigger_autocomplete('#entity-category')
        self.wait()
        autocomplete = self.browser.find_element_by_class_name('ui-autocomplete')

        # Choose category from autocomplete dropdown & save new entity:
        autocomplete.find_element_by_class_name('ui-menu-item-wrapper').click()
        self.browser.find_element_by_id('entity-save').click()
        self.wait()

        # If entity was successfully changed `refresh_btn` should become active:
        refresh_btn = self.browser.find_element_by_id('refresh-table')
        self.assertFalse(refresh_btn.get_attribute('disabled'))

        # After click on `refresh_btn` TE should be updated:
        refresh_btn.click()
        self.browser.find_element_by_id('add-entity').click()
        first_row = self.browser.find_element_by_id('jqGrid').find_element_by_class_name('jqgrow')
        name_cell = first_row.find_elements_by_tag_name('td')[1]
        self.assertEqual(name_cell.get_attribute('title'), new_entity_text)
        self.wait()

        # We are able to change newly created entity:
        self.test_edit_product_name()
