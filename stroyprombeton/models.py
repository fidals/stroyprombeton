"""Models which are specific for stroyprombeton.ru"""

from django.db import models
from django.core.urlresolvers import reverse

from pages.models import SitePageMixin
from catalog.models import AbstractProduct, AbstractCategory
from ecommerce.models import Order as ecOrder


class Order(ecOrder):
    """Extended Order model."""
    company = models.CharField(max_length=255)
    address = models.TextField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)


class Category(AbstractCategory):
    """Extended Category model."""
    specification = models.TextField(blank=True, null=True)
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
    date_price_updated = models.DateField(auto_now_add=True)
    code = models.BigIntegerField(null=True, blank=True)
    mark = models.CharField(max_length=500)
    specification = models.TextField(null=True, blank=True)
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
