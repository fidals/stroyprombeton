from functools import reduce

from django.db import transaction
from django.core.management.base import BaseCommand

from stroyprombeton.models import ProductPage


product_page_content = '''
Производим, продаем и доставляем по России {}.
В Санкт-Петербурге и Москве работает самовывоз.
У нас нет фиксированный цены доставки, поэтому звоните менеджеру, чтобы ее узнать.
Менеджер поможет выбрать способ доставки, рассчитает стоимость и назовет срок.
Следим за тем, чтобы изделия доставляли без дефектов, поэтому даем гарантию.
'''

population_settings = [
    {
        'populate_model': ProductPage,
        'populate_fields': {
            'content': {'template': product_page_content, 'entity_fields': ['name']}
        },
        'exclude': {
            'content__iendswith': product_page_content[-(len(product_page_content) // 3)]
        }
    }
]


@transaction.atomic
def populate_entities(populate_model, populate_fields, exclude=None):
    def populate(entity_, field_name, value):
        if all(field_name in value for field_name in ['entity_fields', 'template']):
            template, entity_fields = value.get('template'), value.get('entity_fields')
            values = [getattr(entity, field_) for field_ in entity_fields]
            setattr(entity_, field_name, template.format(*values))
        elif 'text' in value:
            setattr(entity_, field_name, value)

    exclude = exclude or {}
    entities = populate_model.objects.exclude(**exclude)
    populated_fields = set()

    for entity in entities:
        for field, content in populate_fields.items():
            populated_fields.add(field)
            populate(entity, field, content)
        entity.save()

    if populated_fields:
        populated_fields = reduce(lambda x, y: '{}, {}'.format(x, y), populated_fields)

    print('Was populated {} for {} pages...'.format(populated_fields or '', entities.count()))


class Command(BaseCommand):

    def handle(self, *args, **options):
        for setting in population_settings:
            populate_entities(**setting)
