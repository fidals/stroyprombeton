"""
yml_price command.

Generate two price files: priceru.xml and yandex.yml.
"""
import os
import typing
from urllib.parse import urljoin, urlencode

from django.conf import settings
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string

from stroyprombeton.models import Category, Option


class Command(BaseCommand):
    """Generate yml file for a given vendor (YM or price.ru)."""

    # Online market services, that works with our prices.
    # Dict keys - url targets for every service
    TARGETS = {
        'YM': 'yandex.yml',
    }
    # price files will be stored in this dir
    BASE_DIR = settings.ASSETS_DIR

    def handle(self, *args, **options):
        for utm, file_name in self.TARGETS.items():
            result_file = os.path.join(self.BASE_DIR, file_name)
            self.write_yml(result_file, self.get_context_for_yml(utm))

    @staticmethod
    def get_context_for_yml(utm):
        """Create context dictionary for rendering files."""
        def utm_urls(options) -> typing.Dict[Option, str]:
            """Create mapping from option to UTM url."""
            def url(option):
                utm_params = [
                    ('utm_source', utm),
                    ('utm_medium', 'cpc'),
                    ('utm_content', option.product.get_root_category().page.slug),
                    ('utm_term', option.product.id),
                ]
                url = urljoin(settings.BASE_URL, option.product.url)
                query_string = urlencode(utm_params)
                return f'{url}?{query_string}'

            return {
                option: url(option) for option in options
            }

        categories = Category.objects.all()
        options = (
            Option
            .objects
            .select_related(
                'product',
                'product__page',
                'product__category',
                'product__category__page',
            )
            .filter(product__category__in=categories, price__gt=0)
        )

        return {
            'base_url': settings.BASE_URL,
            'categories': categories,
            'options': options,
            'utm_urls': utm_urls(options),
            'shop': settings.SHOP,
            'utm': utm,
        }

    @staticmethod
    def write_yml(file_to_write, context):
        """Write generated context to file."""
        with open(file_to_write, 'w', encoding='utf-8') as file:
            file.write(render_to_string('ecommerce/prices/price.yml', context).strip())
