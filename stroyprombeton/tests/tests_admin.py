from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.test import TestCase

from pages.models import FlatPage

from stroyprombeton.models import CategoryPage, ProductPage


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
            'product': ['Id', 'Name', 'Category', 'Price', 'Link', 'Is active', ],
            'category': ['Id', 'Name', 'Parent', 'Is active', ],
        }

        cls.fieldsets = {
            'page': [
                'Position', 'Content', 'title', 'Keywords', 'Description', 'Is active', 'Seo text',
                'h1', 'name'
            ],
            'product': [
                'Name', 'Category', 'Price', 'ID', 'Is popular', 'Length', 'Width', 'Height',
                'Weight', 'Volume', 'Diameter out', 'Diameter in', 'Specification', 'code', 'mark'
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
        Pages model's changelist-page must have all needed columns, which was define
        in Admin.py
        """
        response = self.client.get(
            reverse('stb_admin:pages_flatpage_changelist'))

        for field in self.list_display['page']:
            self.assertContains(response, field)

    def test_flat_page_change_fieldset(self):
        """Pages model's change-page must have all needed fields, which was define in Admin.py"""
        response = self.client.get(
            reverse(
                'stb_admin:pages_flatpage_change', args=(FlatPage.objects.filter().first().id, )
            )
        )

        self.assertNotContains(response, 'Products')
        self.assertNotContains(response, 'Categories')

        for field in self.fieldsets['page']:
            self.assertContains(response, field)

    def test_category_page_changelist_display_list(self):
        """
        Categories model's changelist-page must have all needed columns, which was define
        in Admin.py
        """
        response = self.client.get(
            reverse('stb_admin:stroyprombeton_categorypage_changelist'))

        for field in self.list_display['category']:
            self.assertContains(response, field)

    def test_category_page_change_fieldset(self):
        """
        Categories model's change-page must have all needed fields, which was define in Admin.py
        """
        response = self.client.get(
            reverse(
                'stb_admin:stroyprombeton_categorypage_change', args=(
                    CategoryPage.objects.filter().first().id,
                )
            )
        )

        self.assertNotContains(response, 'Products')

        for field in self.fieldsets['category']:
            self.assertContains(response, field)

        for field in self.fieldsets['page']:
            self.assertContains(response, field)

    def test_products_changelist_display_list(self):
        """
        Products model's changelist-page must have all needed columns, which was define
        in Admin.py
        """
        response = self.client.get(
            reverse('stb_admin:stroyprombeton_productpage_changelist'))

        for field in self.list_display['product']:
            self.assertContains(response, field)

    def test_products_change_fieldset(self):
        """Products model's change-page must have all needed fields, which was define in Admin.py"""
        response = self.client.get(
            reverse(
                'stb_admin:stroyprombeton_productpage_change', args=(
                    ProductPage.objects.filter().first().id,
                )
            )
        )

        self.assertNotContains(response, 'Categories')

        for field in self.fieldsets['product']:
            self.assertContains(response, field)

        for field in self.fieldsets['page']:
            self.assertContains(response, field)
