from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from catalog.models import AbstractProduct, AbstractCategory
from ecommerce.models import Order as ecOrder
from mptt import models as mptt_models
from pages import models as page_models


class Order(ecOrder):
    company = models.CharField(max_length=255)
    address = models.TextField(default='', blank=True)
    comment = models.TextField(default='', blank=True)


class Category(AbstractCategory, page_models.PageMixin):
    specification = models.TextField(default='', blank=True)
    link_to_metal = models.URLField(default='', blank=True)

    @classmethod
    def get_default_parent(cls):
        return page_models.CustomPage.objects.filter(slug='gbi').first()

    def get_absolute_url(self):
        """Return url for model."""
        return reverse('category', args=(self.id,))


class Product(AbstractProduct, page_models.PageMixin):
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


class CategoryPage(page_models.ModelPage):
    """Proxy model for Admin"""

    class Meta(page_models.ModelPage.Meta):
        proxy = True

    objects = page_models.ModelPage.create_model_page_managers(Category)


class ProductPage(page_models.ModelPage):
    """Proxy model for Admin"""

    class Meta(page_models.ModelPage.Meta):
        proxy = True

    objects = page_models.ModelPage.create_model_page_managers(Product)


def get_manager(parent_slug):
    class FlatPageTypeManager(mptt_models.TreeManager):
        def get_queryset(self):
            return (
                super(FlatPageTypeManager, self)
                .get_queryset()
                .filter(parent__slug=parent_slug)
            )

    return FlatPageTypeManager()


class NewsForAdmin(page_models.Page):
    class Meta:
        proxy = True
        verbose_name = _('News')
        verbose_name_plural = _('News')

    objects = get_manager('news')


class RegionsForAdmin(page_models.Page):
    class Meta:
        proxy = True
        verbose_name = _('Regions')
        verbose_name_plural = _('Regions')

    objects = get_manager('regions')


class ClientFeedbacksForAdmin(page_models.Page):
    class Meta:
        proxy = True
        verbose_name = _('Client feedbacks')
        verbose_name_plural = _('Client feedbacks')

    objects = get_manager('client-feedbacks')
