"""Models which are specific for stroyprombeton.ru"""

from unidecode import unidecode
from random import randint
from sys import maxsize

from django.utils.text import slugify
from django.db import models
from django.core.urlresolvers import reverse

from catalog.models import AbstractProduct, AbstractCategory
from pages.models import PageMixin, ModelPage, CustomPage, FlatPage
from ecommerce.models import Order as ecOrder


class Order(ecOrder):
    """Extended Order model."""
    company = models.CharField(max_length=255)
    address = models.TextField(default='', blank=True)
    comment = models.TextField(default='', blank=True)


class Category(AbstractCategory, PageMixin):
    """Extended Category model."""
    specification = models.TextField(default='', blank=True)
    link_to_metal = models.URLField(default='', blank=True)

    @classmethod
    def get_default_parent(cls):
        return CustomPage.objects.filter(slug='gbi').first()

    def get_absolute_url(self):
        """Return url for model."""
        return reverse('category', args=(self.id,))


class Product(AbstractProduct, PageMixin):
    """Extended Product model."""
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='products')
    is_new_price = models.NullBooleanField(blank=True, null=True)
    date_price_updated = models.DateField(auto_now_add=True)
    code = models.BigIntegerField(null=True, blank=True)
    mark = models.CharField(default='', max_length=500, blank=True)
    specification = models.TextField(default='', blank=True)
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


class Region(models.Model):
    """Region model - is a region on map (ex: Chelyabinsk region)"""

    name = models.CharField(max_length=255, unique=True)

    def get_absolute_url(self):
        return reverse('region_flat_page', args=(self.page.slug,))


class CategoryPage(ModelPage):
    """Proxy model for Admin"""
    class Meta(ModelPage.Meta):
        proxy = True

    objects = ModelPage.create_model_page_managers(Category)


class ProductPage(ModelPage):
    """Proxy model for Admin"""
    class Meta(ModelPage.Meta):
        proxy = True

    objects = ModelPage.create_model_page_managers(Product)
