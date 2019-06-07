from django.conf import settings
from django.test import TestCase, tag

from catalog import context
from stroyprombeton import models as stb_models


@tag('fast')
class Pagination(TestCase):

    fixtures = ['dump.json']

    def test_options(self):
        category = (
            stb_models.Category.objects
            .filter(products__page__is_active=True)
            .first()
        )
        options = stb_models.Option.objects.filter(
            product__in=category.products.all()
        )
        sliced_options = context.products.PaginatedProducts(
            products=stb_models.Option.objects.filter(
                product__in=category.products.all()
            ),
            url=category.url,
            page_number=1,
            per_page=settings.CATEGORY_STEP_MULTIPLIERS[0],
        )
        sliced, whole = set(sliced_options.products), set(options)
        # every `sliced` is contained in `whole`
        self.assertEqual(sliced, sliced.intersection(whole))
