# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

# https://goo.gl/5qYGp1
flag_symbol = '\U0001F6A9'


def migrate_forward(apps, schema_editor):
    PageTemplate = apps.get_model('pages', 'PageTemplate')

    category_template = PageTemplate.objects.create(
        name='Шаблон страницы категории',
        h1='{{ page.name }}',
        keywords='{{ page.name }}',
        title='{{ page.name }} - низкие цены от производителя. Купить с доставкой по Москве, Санкт-Петербург и всей России',
        description=flag_symbol + ' Купить {{ page.name }} на заводе железобетонных изделий «СТК-Промбетон»',
    )

    product_template = PageTemplate.objects.create(
        name='Шаблон страницы продукта',
        title='{{ page.model.mark }} - {{ page.name }}. Цена: {{ page.model.price }}. {{ page.model.category.specification }}. Купить с доставкой по Москве, Санкт-Петербург и всей России',
        h1='{{ page.name }}',
    )

    Category = apps.get_model('stroyprombeton', 'CategoryPage')
    Product = apps.get_model('stroyprombeton', 'ProductPage')

    Category.objects.filter(template__isnull=True).update(template=category_template)
    Product.objects.filter(template__isnull=True).update(template=product_template)


def migrate_backward(apps, schema_editor):
    PageTemplate = apps.get_model('pages', 'PageTemplate')
    PageTemplate.objects.filter(name__in=[
        'Шаблон страницы категории',
        'Шаблон страницы продукта',
    ]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('stroyprombeton', '0007_remove_category_link_to_metal'),
    ]

    operations = [
        migrations.RunPython(migrate_forward, migrate_backward)
    ]
