"""Models which are specific for stroyprombeton.ru"""

from django.db import models

from seo.models import SitePageMixin
from catalog.models import (Product as AbstractProduct,
                            Category as AbstractCategory)  # TODO: it'll change when they'll be abstract.


class Category(AbstractCategory):
    """Extended Category model."""
    mark = models.CharField(max_length=100)  # TODO: need it?
    link_to_metal = models.URLField(null=True, blank=True)


class Product(AbstractProduct):
    """Extended Product model."""
    is_new_price = models.NullBooleanField()
    date_price_updated = models.DateField(blank=True, null=True)
    nomen = models.BigIntegerField(null=True,
                                   blank=True)  # TODO: need it? Strange name.
    introtext = models.TextField(null=True, blank=True)  # TODO: need it? Strange name.
    mark = models.CharField(max_length=100)
    length = models.IntegerField(null=True, blank=True)
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    volume = models.FloatField(null=True, blank=True)
    diameter_out = models.IntegerField(null=True, blank=True)
    diameter_in = models.IntegerField(null=True, blank=True)


class Territory(SitePageMixin):
    """Territory model - a territory on map (ex: Chelyabinsk region)"""
    slug = models.SlugField(null=True, blank=True)


class Object(SitePageMixin):
    """Object model - constructed object on some Territory (ex.: highway)"""
    slug = models.SlugField(null=True, blank=True)
    territory = models.ForeignKey(Territory)
