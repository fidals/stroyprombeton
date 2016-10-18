"""Models which are specific for stroyprombeton.ru"""

from unidecode import unidecode
from random import randint
from sys import maxsize

from django.utils.text import slugify
from django.db import models
from django.core.urlresolvers import reverse

from catalog.models import AbstractProduct, AbstractCategory
from pages.models import PageConnectorMixin
from ecommerce.models import Order as ecOrder


class Order(ecOrder):
    """Extended Order model."""
    company = models.CharField(max_length=255)
    address = models.TextField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)


class Category(AbstractCategory):
    """Extended Category model."""
    specification = models.TextField(default='', blank=True, null=True)
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
    _slug = models.SlugField(max_length=400)
    is_new_price = models.NullBooleanField(blank=True, null=True)
    date_price_updated = models.DateField(auto_now_add=True)
    code = models.BigIntegerField(null=True, blank=True)
    mark = models.CharField(default='', max_length=500, null=True, blank=True)
    specification = models.TextField(default='', null=True, blank=True)
    length = models.IntegerField(null=True, blank=True)
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    volume = models.FloatField(null=True, blank=True)
    diameter_out = models.IntegerField(null=True, blank=True)
    diameter_in = models.IntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # product slug should be unique, we don't use slug in product url
        self._slug = slugify(unidecode(self.name)) + str(randint(0, maxsize))[1:10]
        super(Product, self).save(*args, **kwargs)

    @property
    def slug(self):
        return self._slug

    def get_absolute_url(self):
        return reverse('product', args=(self.id,))


class Region(PageConnectorMixin):
    """Region model - is a region on map (ex: Chelyabinsk region)"""

    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255)

    @property
    def h1(self):
        return self.name

    @h1.setter
    def h1(self, value):
        # ORM requires any setter
        pass

    def save(self, *args, **kwargs):
        if self.name and not self.slug:
            self.slug = slugify(unidecode(self.name))
        super(Region, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('region_flat_page', args=(self.slug,))
