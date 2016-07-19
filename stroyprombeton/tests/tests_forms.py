from copy import copy
from django.test import TestCase

from stroyprombeton import forms

PRICE_FORM_FIELDS = {
    'name': 'Test',
    'email': 'test@test.test',
    'phone': '+7222222222222',
    'company': 'Test',
    'city': 'Test',
    'activity': 'Производство строительных материалов',
    'site': 'www.test.com'
}

DRAWING_FORM_FIELDS = {
    'name': 'Test',
    'email': 'test@test.test',
    'phone': '+7222222222222',
    'comment': 'Test'
}


class AbstractFormTest:
    REQUIRED = []
    FIELDS = {}
    FORM = None

    def test_empty_form_invalid(self):
        f = self.FORM()
        self.assertFalse(f.is_valid())

    def test_filled_form_valid(self):
        f = self.FORM(self.FIELDS)
        self.assertTrue(f.is_valid())

    def test_missed_required_field(self):
        for req_field in self.REQUIRED:
            wrong = {req_field: ''}
            fields = self.FIELDS.update(wrong)
            self.assertFalse(self.FORM(fields).is_valid())


class PriceFormTest(AbstractFormTest, TestCase):
    REQUIRED = ['phone', 'email', 'company', 'city', 'activity']
    FIELDS = copy(PRICE_FORM_FIELDS)
    FORM = forms.PriceForm

    def test_wrong_activity_invalid(self):
        wrong_activity = {'activity': 'Test'}
        f = forms.PriceForm(self.FIELDS.update(wrong_activity))
        self.assertFalse(f.is_valid())

    def test_invalid_email(self):
        self.FIELDS['email'] = 'n@t.a.em@il'
        self.assertFalse(forms.PriceForm(self.FIELDS).is_valid())

    def test_invalid_site(self):
        self.FIELDS['site'] = 'n@t.a.s/te'
        self.assertFalse(forms.PriceForm(self.FIELDS).is_valid())


class DrawingFormTest(AbstractFormTest, TestCase):
    REQUIRED = ['phone', 'email']
    FIELDS = copy(DRAWING_FORM_FIELDS)
    FORM = forms.DrawingForm

    def test_invalid_email(self):
        self.FIELDS['email'] = 'n@t.a.em@il'
        self.assertFalse(self.FORM(self.FIELDS).is_valid())
