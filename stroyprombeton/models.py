from django.db import models
from django.urls import reverse

from catalog.models import AbstractProduct, AbstractCategory
from ecommerce.models import Order as ecOrder
from pages.models import PageMixin, ModelPage, CustomPage, FlatPage


class Order(ecOrder):
    company = models.CharField(max_length=255)
    address = models.TextField(default='', blank=True)
    comment = models.TextField(default='', blank=True)


class Category(AbstractCategory, PageMixin):
    specification = models.TextField(default='', blank=True)
    link_to_metal = models.URLField(default='', blank=True)

    @classmethod
    def get_default_parent(cls):
        return CustomPage.objects.filter(slug='gbi').first()

    def get_absolute_url(self):
        """Return url for model."""
        return reverse('category', args=(self.id,))


class Product(AbstractProduct, PageMixin):
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

    def get_absolute_url(self):
        return reverse('product', args=(self.id,))


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
