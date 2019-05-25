from django.test import TestCase, tag

from pages import models as pages_models
from stroyprombeton import models as stb_models


@tag('fast')
class Category_(TestCase):

    fixtures = ['dump.json']

    def test_series(self):
        option = stb_models.Option.objects.first()
        least = option.product.category
        root = least.get_root()
        self.assertIn(option.series, least.get_series())
        self.assertIn(option.series, root.get_series())


@tag('fast')
class Option_(TestCase):

    def get_min_price_test_box(self, in_prices, out_price):
        product = stb_models.Product.objects.create(
            name='some_name',
            category=stb_models.Category.objects.create(name='some_name'),
            page=pages_models.Page.objects.create(
                name='some_name',
                is_active=True,
            )
        )
        options = [
            stb_models.Option.objects.create(
                mark='some_mark',
                price=price,
                product=product,
            ) for price in in_prices
        ]
        qs = stb_models.Option.objects.filter(id__in=[o.id for o in options])
        self.assertEqual(out_price, qs.min_price())
        # page is not deleted by products cascade by unknown for me reason
        product.page.delete()
        product.category.delete()

    def test_get_min_price(self):
        self.get_min_price_test_box(in_prices=[], out_price=0.0)
        self.get_min_price_test_box(in_prices=[0.0], out_price=0.0)
        self.get_min_price_test_box(in_prices=[20.0, 10.0], out_price=10.0)
