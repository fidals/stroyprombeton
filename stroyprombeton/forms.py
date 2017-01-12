from functools import reduce

from django import forms
from django.core.exceptions import ValidationError
from django.forms import NumberInput, TextInput, Textarea
from django.template.defaultfilters import filesizeformat

from stroyprombeton.models import Order, Product


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


class FileValidation:

    error_messages = {
        'max_size': ('Размер файла больше %(max_size)s.'
                     ' Размер текущего файла %(size)s.'),
        'max_count': ('Количесвто фалов больше %(max_count)s.'
                      ' Количество текущих файлов %(count)s.'),
        'content_type': 'Файла формата %(content_type)s не поддерживается.',
    }

    def __init__(self, max_size=1024 * 1024 * 20, max_count=None, content_types=None):
        self.max_size = max_size
        self.max_count = max_count
        self.content_types = content_types

    def __call__(self, data):
        if self.max_size is not None and self.max_size < data.size:
            raise ValidationError(
                message=self.error_messages['max_size'],
                code='max_size',
                params={
                    'max_size': filesizeformat(self.max_size),
                    'size': filesizeformat(data.size)
                }
            )

        if self.content_types and data.content_type not in self.content_types:
            raise ValidationError(
                message=self.error_messages['content_type'],
                code='content_type',
                params={'content_type': data.content_type}
            )

    def validate_files(self, files):
        """Validate multiple files."""
        files_count = len(files)
        if self.max_count and files_count > self.max_count:
            raise ValidationError(
                message=self.error_messages['max_count'],
                code='max_count',
                params={
                    'max_count': self.max_count,
                    'count': files_count
                }
            )

        for file in files:
            self(file)


class BaseContactForm(forms.Form):
    """Define basic information about customer."""

    css_class = {'class': 'input-field'}
    required_error_message = {'required': 'Пожалуйста, заполните это поле.'}

    name = forms.CharField(
        label='Имя',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs=css_class)
    )

    phone = forms.CharField(
        label='Телефон',
        max_length=20,
        error_messages=required_error_message,
        widget=forms.TextInput(attrs={
            'class': 'input-field js-input-field js-masked-phone',
            'placeholder': '+7 (999) 000 00 00',
        })
    )

    email = forms.EmailField(
        label='Электронная почта',
        error_messages={
            **required_error_message,
            'invalid': 'Пожалуйста, введите корректный адрес электроной почты.'
        },
        widget=forms.EmailInput(attrs={
            **css_class,
            'type': 'email',
        })
    )


class PriceForm(BaseContactForm):
    """Form for Price List ordering."""

    company = forms.CharField(
        label='Полное название организации *',
        max_length=100,
        error_messages=BaseContactForm.required_error_message
    )

    city = forms.CharField(
        label='Город *',
        max_length=100,
        error_messages=BaseContactForm.required_error_message
    )

    activity = forms.ChoiceField(
        label='Направление деятельности организации *',
        choices=generate_activities,
        error_messages=BaseContactForm.required_error_message
    )

    site = forms.URLField(label='Сайт', required=False)


class DrawingForm(BaseContactForm):
    """Form for Drawing order."""

    accept_mime_types = [
        'image/jpeg', 'image/png', 'image/gif', 'image/tiff', 'application/pdf',
        'application/zip', 'application/x-7z-compressed', 'application/x-tar',
        'application/x-rar-compressed', 'application/msword', 'application/vnd.ms-excel',
    ]

    file = forms.FileField(
        label='Прикрепить файл',
        required=False,
        help_text='''Максимальный размер файла - 20 Мб.
        Вы можете прикрепить не более 10 вложений одновременно. Допустимые форматы вложений:
        jpeg, pdf, tiff, gif, doc, xls, zip, 7-zip, rar, tar.''',
        widget=forms.ClearableFileInput(
            attrs={
                'class': 'js-file-input input-field',
                'accept': str(reduce(lambda x, y: '{},{}'.format(x, y), accept_mime_types)),
                'multiple': 'True'
            }
        ),
    )

    comment = forms.CharField(
        label='Комментарий',
        required=False,
        widget=forms.Textarea(attrs=BaseContactForm.css_class)
    )

    def clean(self):
        if self.files:
            files_validator = FileValidation(max_count=10, content_types=self.accept_mime_types)

            try:
                files_validator.validate_files(self.files.getlist('file'))
            except ValidationError as e:
                self.add_error('file', e)

        return super(DrawingForm, self).clean()


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
                    'id': 'entity-name',
                    'class': 'form-control js-new-entity js-required'
                }),
            'category': TextInput(
                attrs={
                    'id': 'entity-category',
                    'class': 'form-control js-new-entity js-required'
                }),
            'price': NumberInput(
                attrs={
                    'id': 'entity-price',
                    'class': 'form-control js-new-entity',
                    'max': '1000000.00',
                    'min': '0.00',
                    'pattern': '[0-9]',
                    'step': '1.00'
                })
        }
