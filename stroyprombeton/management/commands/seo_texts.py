from functools import reduce
from operator import or_

from django.db import transaction
from django.db.models.expressions import Q
from django.core.management.base import BaseCommand

from stroyprombeton.models import ProductPage, CategoryPage

# https://goo.gl/5qYGp1
flag_symbol = '\U0001F6A9'

product_page = {
    'content': '''
Производим, продаем и доставляем по России {}.
В Санкт-Петербурге и Ленинградской области работает самовывоз.
У нас нет фиксированный цены доставки, поэтому звоните менеджеру, чтобы ее узнать.
Менеджер поможет выбрать способ доставки, рассчитает стоимость и назовет срок.
Следим за тем, чтобы изделия доставляли без дефектов, поэтому даем гарантию.''',
    'title': '{} - {}. Цена: {}. Купить с доставкой по Москве, Санкт-Петербург и всей России.',
    'keywords': '{}',
    'description': flag_symbol + ' Купить {} на заводе железобетонных изделий "СТК-Промбетон"',
}

category_page = {
    'title': '{} - низкие цены от производителя. Купить с доставкой по Москве, Санкт-Петербург и '
             'всей России',
    'description': flag_symbol + ' Купить {} на заводе железобетонных изделий «СТК-Промбетон»',
    'keywords': '{}',
}

population_settings = [
    {
        'populate_model': CategoryPage,
        'populate_fields': {
            'title': {
                'template': {
                    'text': category_page['title'],
                    'variables': ['h1'],
                },
            },
            'description': {
                'template': {
                    'text': category_page['description'],
                    'variables': ['h1'],
                },
            },
            'keywords': {
                'template': {
                    'text': category_page['keywords'],
                    'variables': ['h1'],
                },
            },
        },
    },
    {
        'populate_model': ProductPage,
        'populate_fields': {
            'content': {
                'template': {
                    'text': product_page['content'],
                    'variables': ['name'],
                },
            },
            'title': {
                'template': {
                    'text': product_page['title'],
                    'variables': ['model.mark', 'name', 'model.price'],
                    'correction': {
                        'model.price': (
                            lambda e, v: v + ' руб'
                            if not float(v) == 0 else
                            'по запросу'
                        ),
                        'name': lambda e, v: v.replace(e.model.mark, ''),
                    }
                },
            },
            'description': {
                'template': {
                    'text': product_page['description'],
                    'variables': ['name'],
                },
            },
            'keywords': {
                'template': {
                    'text': product_page['keywords'],
                    'variables': ['name', 'model.mark'],
                },
            },
        },
    },
]


@transaction.atomic
def populate_entities(populate_model, populate_fields, overwrite=False):
    def get_by_attrs(entity_, attrs: str) -> str:
        """
        Get value for template from attribute chain.
        >>> entity_ = ProductPage.objects.get(parent__name='Pipe')
        >>> get_by_attrs(entity_,'model.category.page.name')
        >>> 'Pipe'
        """
        return str(reduce(getattr, attrs.split('.'), entity_))

    def get_template_value(entity_, field_name_, correction=None):
        if '.' in field_name_:
            value = get_by_attrs(entity_, field_name_)
        else:
            value = getattr(entity_, field_name_, '')

        if correction and field_name_ in correction:
            value = correction[field_name_](entity_, value)

        return value.strip()

    def populate(entity_, field_name_, template):
        text, entity_fields, correction = (
            template.get('text'), template.get('variables'), template.get('correction')
        )

        values = [
            get_template_value(entity_, field, correction)
            for field in entity_fields
        ]

        setattr(entity_, field_name_, text.format(*values))

    populated_fields = set()

    if not overwrite:
        entities = populate_model.objects.filter(
            reduce(or_, (Q(**{k: ''}) for k in populate_fields.keys()))
        )
    else:
        entities = populate_model.objects.all()

    for entity in entities.iterator():
        for field_name, fields_populate_settings in populate_fields.items():
            populate(entity, field_name, fields_populate_settings.get('template'))
            entity.save()

            populated_fields.add(field_name)

    if populated_fields:
        populated_fields = reduce('{}, {}'.format, populated_fields)
        print('Was populated {} for {}...'.format(
            populated_fields, populate_model._meta.model_name
        ))


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--overwrite',
            action='store_true',
            dest='overwrite',
            default=False,
            help='Overwrite all seo fields.'
        )

    def handle(self, *args, **options):
        for setting in population_settings:
            populate_entities(**setting, overwrite=options['overwrite'])
