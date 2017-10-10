from django.db import transaction
from django.db.models import Count
from django.core.management.base import BaseCommand

from stroyprombeton.models import Product


class Command(BaseCommand):
    """
    Remove products with similar values in given columns.

    E.g. with similar serial number or other technical id.
    """

    def add_arguments(self, parser):
        parser.add_argument('columns', nargs='+', type=str)
        parser.add_argument('--noinput', dest='noinput', action='store_false')

    @transaction.atomic
    def handle(self, *args, **options):
        columns = options.get('columns')
        duplicates = (
            Product
            .objects
            .values(*columns)
            .annotate(Count('id'))
            .order_by()
            .filter(id__count__gt=1)
        )
        # I think it's OK to ask user permission before doing such actions
        # (until we'll have everyday backups or something similar)
        question = f'We\'re going to modify ~{duplicates.count()} products'
        if not options.get('noinput'):
            answer = input(f'{question}. Is it OK (yes/no):').lower()
        else:
            answer = 'yes'
        if answer in {'yes', 'y'}:
            for duplicate in duplicates:
                # remove column that doesn't really exist
                # they added by result of aggregation query
                del duplicate['id__count']
                (
                    Product
                    .objects
                    .filter(**duplicate)
                    .first()
                    .delete()
                )
