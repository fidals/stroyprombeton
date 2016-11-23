from django import forms
from django.forms import TextInput, Textarea

from stroyprombeton.models import Order


def generate_activities():
    """
    Get a tuple of a possible company's activities.

    Format:
        ((A, A), (B, B))
    to use in Django forms.
    """

    activities = ('Подрядная строительная организация',
                  'Производство строительных материалов',
                  'Проектная организация',
                  'Заказчик',
                  'Оптовая торговля')

    return tuple((a, a) for a in activities)


class BaseContactForm(forms.Form):
    """Define basic information about customer."""

    name = forms.CharField(label='Имя *', max_length=100, required=False)
    phone = forms.CharField(label='Телефон *', max_length=100)
    email = forms.EmailField(label='Электронная почта *')


class PriceForm(BaseContactForm):
    """Form for Price List ordering."""

    company = forms.CharField(label='Полное название организации *',
                              max_length=100)
    city = forms.CharField(label='Город *',
                           max_length=100)
    activity = forms.ChoiceField(label='Направление деятельности организации *',
                                 choices=generate_activities)
    site = forms.URLField(label='Сайт', required=False)


class DrawingForm(BaseContactForm):
    """Form for order drawing."""

    comment = forms.CharField(
        label='Комментарий',
        widget=forms.Textarea,
        required=False
    )


class OrderForm(forms.ModelForm):
    """
    Form for making orders. Based on Order model.

    Define required contact information about a customer.
    """

    class Meta:
        model = Order
        fields = [
            'name',
            'phone',
            'email',
            'company',
            'address',
            'comment'
        ]

        widgets = {
            'name': TextInput(attrs={'class': 'input-field order-input-field js-input-field'}),
            'phone': TextInput(attrs={'class': 'input-field order-input-field js-input-field'}),
            'email': TextInput(attrs={'class': 'input-field order-input-field js-input-field'}),
            'company': TextInput(attrs={'class': 'input-field order-input-field js-input-field'}),
            'address': Textarea(attrs={'class': 'js-input-field'}),
            'comment': Textarea(attrs={'class': 'js-input-field'}),
        }
