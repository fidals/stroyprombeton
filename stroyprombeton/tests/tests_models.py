from django.test import TestCase, tag

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
