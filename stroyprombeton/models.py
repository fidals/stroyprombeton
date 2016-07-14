"""Models which are specific for stroyprombeton.ru"""

from django.db import models
from django.core.urlresolvers import reverse

from pages.models import SitePageMixin
from catalog.models import AbstractProduct, AbstractCategory


class Category(AbstractCategory):
    """Extended Category model."""
    specification = models.CharField(max_length=1000, blank=True, null=True)
    link_to_metal = models.URLField(null=True, blank=True)

    product_relation = 'product'

    def get_absolute_url(self):
        """Return url for model."""
        return reverse('category', args=(self.id,))


class Product(AbstractProduct):
    """Extended Product model."""
    category = models.ForeignKey(Category,
                                 on_delete=models.CASCADE,
                                 related_name='products')
    is_new_price = models.NullBooleanField(blank=True, null=True)
    date_price_updated = models.DateField()
    code = models.BigIntegerField(null=True, blank=True)
    mark = models.CharField(max_length=100)
    specification = models.CharField(max_length=1000, null=True, blank=True)
    length = models.IntegerField(null=True, blank=True)
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    volume = models.FloatField(null=True, blank=True)
    diameter_out = models.IntegerField(null=True, blank=True)
    diameter_in = models.IntegerField(null=True, blank=True)

    def get_absolute_url(self):
        return reverse('product', args=(self.id,))


class Static_page(SitePageMixin):
    slug = models.SlugField(null=True, blank=True)


class Territory(SitePageMixin):
    """Territory model - a territory on map (ex: Chelyabinsk region)"""
    slug = models.SlugField(null=True, blank=True)


class Object(SitePageMixin):
    """Object model - constructed object on some Territory (ex.: highway)"""
    slug = models.SlugField(null=True, blank=True)
    territory = models.ForeignKey(Territory)
