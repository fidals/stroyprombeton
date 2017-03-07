from django import forms
from django.forms import NumberInput, TextInput, Textarea

from stroyprombeton.models import Order, Product

phone_validation_pattern = (
    '(\+\d\s|\+\d)\(?\d{3}(\)|\)\s)?-?\d{1}-?\d{1}-?(\d{1}|\d{1}\s)-?\d{1}-?(\d{1}|\d{'
    '1}\s)-?\d{1}-?\d{1}'
)
css_default_classes = 'input-field js-input-field '
css_required_classes = css_default_classes + 'input-required '


def generate_activities():
    """
    Get a tuple of a possible company's activities.

    Format:
        ((A, A), (B, B))
    to use in Django forms.
    """
    activities = (
        'Подрядная строительная организация',
        'Производство строительных материалов',
        'Проектная организация',
        'Заказчик',
        'Оптовая торговля'
    )

    return tuple((a, a) for a in activities)


class BaseContactForm(forms.Form):
    """Define basic information about customer."""

    required_error_message = {'required': 'Пожалуйста, заполните это поле.'}

    name = forms.CharField(
        label='Имя',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': css_default_classes,
        }),
    )

    phone = forms.CharField(
        label='Телефон',
        max_length=20,
        error_messages=required_error_message,
        widget=forms.TextInput(attrs={
            'class': css_required_classes + 'js-masked-phone',
            'pattern': phone_validation_pattern,
            'placeholder': '+7 (999) 000 00 00',
            'required': True,
        }),
    )

    email = forms.EmailField(
        label='Электронная почта',
        error_messages={
            **required_error_message,
            'invalid': 'Пожалуйста, введите корректный адрес электроной почты.',
        },
        widget=forms.EmailInput(attrs={
            'class': css_required_classes,
            'type': 'email',
            'required': True,
        }),
    )


class PriceForm(BaseContactForm):
    """Form for Price List ordering."""

    company = forms.CharField(
        label='Полное название организации',
        max_length=100,
        error_messages=BaseContactForm.required_error_message,
        widget=forms.TextInput(attrs={
            'class': css_required_classes,
            'required': True,
        }),
    )

    city = forms.CharField(
        label='Город',
        max_length=100,
        error_messages=BaseContactForm.required_error_message,
        widget=forms.TextInput(attrs={
            'class': css_required_classes + 'js-city',
            'required': True,
        }),
    )

    activity = forms.ChoiceField(
        label='Направление деятельности организации',
        choices=generate_activities,
        error_messages=BaseContactForm.required_error_message,
    )

    site = forms.URLField(
        label='Сайт',
        widget=forms.TextInput(attrs={
            'class': css_default_classes,
            'required': False,
        }),
    )


class DrawingForm(BaseContactForm):
    """Form for Drawing order."""

    comment = forms.CharField(
        label='Комментарий',
        required=False,
        widget=forms.Textarea(attrs={
            'class': css_default_classes
        })
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
            'name': TextInput(attrs={'class': css_default_classes}),
            'phone': TextInput(attrs={
                'class': css_required_classes,
                'pattern': phone_validation_pattern,
                'required': True
            }),
            'email': TextInput(attrs={
                'class': css_required_classes,
                'type': 'email',
                'required': True
            }),
            'company': TextInput(attrs={
                'class': css_required_classes,
                'required': True
            }),
            'address': Textarea(attrs={'class': 'js-input-field'}),
            'comment': Textarea(attrs={'class': 'js-input-field'}),
        }


class AddProductForm(forms.ModelForm):
    """Form for adding new Product in Table Editor."""

    class Meta:
        model = Product
        fields = [
            'name',
            'category',
            'price'
        ]

        widgets = {
            'name': TextInput(
                attrs={
                    'class': 'form-control js-required',
                    'data-id': 'name',
                    'id': 'entity-name'
                }),
            'category': TextInput(
                attrs={
                    'class': 'form-control js-required',
                    'data-id': 'category',
                    'id': 'entity-category'
                }),
            'price': NumberInput(
                attrs={
                    'class': 'form-control js-required',
                    'data-id': 'price',
                    'id': 'entity-price',
                    'max': '1000000.00',
                    'min': '0.00',
                    'pattern': '[0-9]',
                    'step': '1.00'
                })
        }
