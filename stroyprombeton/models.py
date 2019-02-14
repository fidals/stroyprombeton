import mptt
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

import catalog
import pages
from ecommerce.models import Order as ecOrder


class Order(ecOrder):
    company = models.CharField(max_length=255, verbose_name='company')
    address = models.TextField(default='', blank=True, verbose_name='address')
    comment = models.TextField(default='', blank=True, verbose_name='comment')


# @todo #rf169 Fix model.Manager inheritance problem
#  Category model ignores parent's manager.
#  ```
#  In [1]: from stroyprombeton.models import Category
#
#  In [2]: type(Category.objects)
#  Out[2]: mptt.managers.TreeManager
#  ```
#  Should be `catalog.models.CategoryManager`
#
#  Then use model.Manager.active() filter everywhere in this project (rf#169).
class Category(catalog.models.AbstractCategory, pages.models.PageMixin):
    specification = models.TextField(
        default='',
        blank=True,
        verbose_name=_('specification'),
    )

    @classmethod
    def get_default_parent(cls):
        return pages.models.CustomPage.objects.filter(slug='gbi').first()

    def get_absolute_url(self):
        """Return url for model."""
        return reverse('category', args=(self.id,))


class Option(models.Model):
    """This doc page describes what is option: https://goo.gl/S4U9PG."""

    @property
    def name(self):
        return self.product.name

    @property
    def page(self):
        return self.product.page

    def get_absolute_url(self):
        return self.product.url

    @property
    def url(self):
        return self.product.url

    tags = models.ManyToManyField(
        'Tag',
        related_name='options',
        blank=True,
        null=True,
        verbose_name=_('tags'),
    )
    product = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='options',
        verbose_name=_('product'),
    )
    date_price_updated = models.DateField(auto_now_add=True, verbose_name=_('date price updated'))
    is_new_price = models.NullBooleanField(
        blank=True,
        null=True,
        verbose_name=_('is new price'),  # Ignore CPDBear
    )
    price = models.FloatField(
        blank=True,
        default=0,
        db_index=True,
        verbose_name=_('price'),
    )
    in_stock = models.PositiveIntegerField(
        default=0,
        db_index=True,
        verbose_name=_('in stock'),
    )
    is_popular = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name=_('is popular'),
    )

    def __str__(self):
        return self.mark  # Ignore CPDBear

    # this fields will be moved to tags after Tags feature will be finished.
    # See https://github.com/fidals/stroyprombeton/labels/Tags
    code = models.BigIntegerField(null=True, blank=True, verbose_name=_('code'))  # Ignore CPDBear
    mark = models.CharField(default='', max_length=500, blank=True, verbose_name=_('mark'))
    specification = models.TextField(default='', blank=True, verbose_name=_('specification'),)
    length = models.IntegerField(null=True, blank=True, verbose_name=_('length'))
    width = models.IntegerField(null=True, blank=True, verbose_name=_('width'))
    height = models.IntegerField(null=True, blank=True, verbose_name=_('height'))
    weight = models.FloatField(null=True, blank=True, verbose_name=_('weight'))
    volume = models.FloatField(null=True, blank=True, verbose_name=_('volume'))
    diameter_out = models.IntegerField(null=True, blank=True, verbose_name=_('diameter out'))
    diameter_in = models.IntegerField(null=True, blank=True, verbose_name=_('diameter in'))


# not inherited from `catalog.models.AbstractProduct`, because
# AbstractProduct's set of fields is shared between Product and Option models.
class Product(catalog.models.AbstractProduct, pages.models.PageMixin):
    objects = catalog.models.ProductManager()

    name = models.CharField(max_length=255, db_index=True, verbose_name=_('name'))
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name=_('category'),
    )

    def __str__(self):
        return self.name

    @property
    def url(self):
        return self.get_absolute_url()

    @property
    def parent(self):
        return self.category or None

    def get_absolute_url(self):
        return reverse('product', args=(self.id,))

    def get_admin_tree_title(self):
        return f'[{self.id}] {self.name} {self.mark}]'

    def get_root_category(self):
        return self.category.get_root()

    def get_siblings(self, offset):
        return (
            self.__class__.objects
            .active()
            .filter(category=self.category)
            .exclude(id=self.id)
            .prefetch_related('category')
            .select_related('page')[:offset]
        )

    # we'll remove this fields from Product model
    # after adapting all system components Options model.
    # This set of github issues should be finished for removing the fields:
    # https://github.com/fidals/stroyprombeton/labels/Product%20options
    is_new_price = models.NullBooleanField(
        blank=True,
        null=True,
        verbose_name=_('is new price'),
    )
    tags = models.ManyToManyField(
        'Tag',
        related_name='products',
        blank=True,
        null=True,
        verbose_name=_('tags'),
    )
    price = models.FloatField(
        blank=True,
        default=0,
        db_index=True,
        verbose_name=_('price'),
    )
    in_stock = models.PositiveIntegerField(
        default=0,
        db_index=True,
        verbose_name=_('in stock'),
    )
    is_popular = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name=_('is popular'),
    )

    date_price_updated = models.DateField(auto_now_add=True, verbose_name=_('date price updated'))
    code = models.BigIntegerField(null=True, blank=True, verbose_name=_('code'))
    mark = models.CharField(default='', max_length=500, blank=True, verbose_name=_('mark'))
    specification = models.TextField(default='', blank=True, verbose_name=_('specification'),)
    length = models.IntegerField(null=True, blank=True, verbose_name=_('length'))
    width = models.IntegerField(null=True, blank=True, verbose_name=_('width'))
    height = models.IntegerField(null=True, blank=True, verbose_name=_('height'))
    weight = models.FloatField(null=True, blank=True, verbose_name=_('weight'))
    volume = models.FloatField(null=True, blank=True, verbose_name=_('volume'))
    diameter_out = models.IntegerField(null=True, blank=True, verbose_name=_('diameter out'))
    diameter_in = models.IntegerField(null=True, blank=True, verbose_name=_('diameter in'))


class CategoryPage(pages.models.ModelPage):
    """Proxy model for Admin."""

    class Meta(pages.models.ModelPage.Meta):
        proxy = True
        verbose_name = _('category')
        verbose_name_plural = _('categories')

    objects = pages.models.ModelPage.create_model_page_managers(Category)


class ProductPage(pages.models.ModelPage):
    """Proxy model for Admin."""

    class Meta(pages.models.ModelPage.Meta):
        proxy = True
        verbose_name = _('product')
        verbose_name_plural = _('products')

    objects = pages.models.ModelPage.create_model_page_managers(Product)


def get_manager(parent_slug):
    class FlatPageTypeManager(mptt.models.TreeManager):
        def get_queryset(self):
            return (
                super(FlatPageTypeManager, self)
                .get_queryset()
                .filter(parent__slug=parent_slug)
            )

    return FlatPageTypeManager()


# @todo #172:60m Set "news" parent-page by default.
#  At stb#172 PO had problems with creating news.
#  Then dev should do 1h research to reinvent
#  manually adding "news" parent-page rule.
class NewsForAdmin(pages.models.Page):
    class Meta:
        proxy = True
        verbose_name = _('News')
        verbose_name_plural = _('News')

    objects = get_manager('news')


class RegionsForAdmin(pages.models.Page):
    class Meta:
        proxy = True
        verbose_name = _('Regions')
        verbose_name_plural = _('Regions')

    objects = get_manager('regions')


class ClientFeedbacksForAdmin(pages.models.Page):
    class Meta:
        proxy = True
        verbose_name = _('Client feedbacks')
        verbose_name_plural = _('Client feedbacks')

    objects = get_manager('client-feedbacks')


class TagGroup(catalog.models.TagGroup):
    pass


class TagQuerySet(catalog.models.TagQuerySet):
    pass


class Tag(catalog.models.Tag):
    group = models.ForeignKey(
        TagGroup, on_delete=models.CASCADE, null=True, related_name='tags',
    )
