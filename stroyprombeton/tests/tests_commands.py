from django.test import TestCase

from pages.models import Page

from stroyprombeton.management.commands.seo_texts import populate_entities


class SeoTexts(TestCase):

    setting = {
        'populate_model': Page,
        'populate_fields': {},
        'exclude': {
            'content__istartswith': 'just'
        }
    }

    def setUp(self):
        self.first_page = Page.objects.create(name='First', content='Just q')
        self.second_page = Page.objects.create(name='Second')

    def tearDown(self):
        self.first_page.delete()
        self.second_page.delete()

    def test_populate_entities_by_template(self):
        first_page_content = self.first_page.content
        second_page_content = self.second_page.content

        self.setting.update(populate_fields={'content': {'template': 'It is {}', 'entity_fields': ['name']}})

        populate_entities(**self.setting)

        self.setting.update(populate_fields={})

        test_first_page_content = Page.objects.get(name=self.first_page.name).content
        test_second_page_content = Page.objects.get(name=self.second_page.name).content

        self.assertEqual(first_page_content, test_first_page_content)
        self.assertNotEqual(second_page_content, test_second_page_content)

    def test_populate_entities_by_text(self):
        first_page_content = self.first_page.content
        second_page_content = self.second_page.content

        self.setting.update(populate_fields={'content': {'text': 'It is second page'}})

        populate_entities(**self.setting)

        self.setting.update(populate_fields={})

        test_first_page_content = Page.objects.get(name=self.first_page.name).content
        test_second_page_content = Page.objects.get(name=self.second_page.name).content

        self.assertEqual(first_page_content, test_first_page_content)
        self.assertNotEqual(second_page_content, test_second_page_content)
