from django.contrib.auth.models import User
from django.test import TestCase, tag
from django.urls import reverse

from pages.models import FlatPage
from stroyprombeton.models import CategoryPage, ProductPage


@tag('fast')
class AdminPage(TestCase):
    """Tests for Admin page UI."""

    fixtures = ['dump.json']

    @classmethod
    def setUpClass(cls):
        super(AdminPage, cls).setUpClass()
        cls.username = 'admin'
        cls.email = 'admin@admin.com'
        cls.password = 'asdfjkl'

        cls.list_display = {
            'page': ['ID', 'Name', 'Parent', 'Is active', ],
            'product': ['Id', 'Name', 'Category', 'Link', 'Is active', ],
            'category': ['Id', 'Name', 'Parent', 'Is active', ],
        }

        cls.fieldsets = {
            'page': [
                'Position', 'Content', 'title', 'Keywords', 'Description', 'Is active', 'Seo text',
                'h1', 'name'
            ],
            'product': [
                'Name', 'Category', 'ID',
            ],
            'category': ['Name', 'Parent', 'Position', 'ID', ],
        }

    def setUp(self):
        self.user = User.objects.create_superuser(self.username, self.email, self.password)
        self.client.login(username=self.username, password=self.password)

    def tearDown(self):
        self.user.delete()

    def test_flat_page_changelist_display_list(self):
        """
        Test a changelist-page required columns.

        Pages model's changelist-page must have all needed columns, which was
        define in Admin.py.
        """
        response = self.client.get(
            reverse('stb_admin:pages_flatpage_changelist'))

        for field in self.list_display['page']:
            self.assertContains(response, field)

    def test_flat_page_change_fieldset(self):
        """
        Test a change-page required fields.

        Pages model's change-page must have all needed fields, which was
        define in Admin.py.
        """
        response = self.client.get(
            reverse(
                'stb_admin:pages_flatpage_change', args=(FlatPage.objects.all().first().id, )
            )
        )

        for field in self.fieldsets['page']:
            self.assertContains(response, field)

    def test_category_page_changelist_display_list(self):
        """
        Test a changelist-page required columns.

        Categories model's changelist-page must have all needed columns, which
        was define in Admin.py.
        """
        response = self.client.get(
            reverse('stb_admin:stroyprombeton_categorypage_changelist'))

        for field in self.list_display['category']:
            self.assertContains(response, field)

    def test_category_page_change_fieldset(self):
        """
        Test a change-page required fields.

        Categories model's change-page must have all needed fields, which was
        define in Admin.py.
        """
        response = self.client.get(
            reverse(
                'stb_admin:stroyprombeton_categorypage_change', args=(
                    CategoryPage.objects.filter().first().id,
                )
            )
        )

        for field in self.fieldsets['category']:
            self.assertContains(response, field)

        for field in self.fieldsets['page']:
            self.assertContains(response, field)

    def test_products_changelist_display_list(self):
        """
        Test a changelist-page required columns.

        Products model's changelist-page must have all needed columns, which
        was define in Admin.py.
        """
        response = self.client.get(
            reverse('stb_admin:stroyprombeton_productpage_changelist'))

        for field in self.list_display['product']:
            self.assertContains(response, field)

    def test_products_change_fieldset(self):
        """
        Test a change-page required fields.

        Products model's change-page must have all needed fields, which was
        define in Admin.py.
        """
        response = self.client.get(
            reverse(
                'stb_admin:stroyprombeton_productpage_change', args=(
                    ProductPage.objects.filter().first().id,
                )
            )
        )

        for field in self.fieldsets['product']:
            self.assertContains(response, field)

        for field in self.fieldsets['page']:
            self.assertContains(response, field)
