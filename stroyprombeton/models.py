import typing

import mptt
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

import catalog
import ecommerce
import pages


class Order(ecommerce.models.Order):
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
    # @todo #483:30m  Explore `Category.specification` field purpose.
    #  Then document or rename it.
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


class OptionQuerySet(models.QuerySet):

    def active(self):
        return self.filter(product__isnull=False, product__page__is_active=True)

    def bind_fields(self):
        """Prefetch or select typical related fields to reduce sql queries count."""
        return (
            self.select_related('product')
            .prefetch_related('tags')
        )

    def filter_descendants(self, category: models.Model) -> models.QuerySet:
        return self.filter(product__category__in=category.get_descendants(True))

    def tagged(self, tags: 'TagQuerySet'):
        # Distinct because a relation of tags and products is M2M.
        # We do not specify the args for `distinct` to avoid dependencies
        # between `order_by` and `distinct` methods.

        # Postgres has `SELECT DISTINCT ON`, that depends on `ORDER BY`.
        # See docs for details:
        # https://www.postgresql.org/docs/10/static/sql-select.html#SQL-DISTINCT
        # https://docs.djangoproject.com/en/2.1/ref/models/querysets/#django.db.models.query.QuerySet.distinct
        return self.filter(tags__in=tags).distinct()

    def tagged_or_all(self, tags: 'TagQuerySet'):
        return (
            self.tagged(tags)
            if tags.exists()
            else self
        )


class OptionManager(models.Manager.from_queryset(OptionQuerySet)):
    """Get all products of given category by Category's id or instance."""


class Option(models.Model):
    """This doc page describes what is option: https://goo.gl/S4U9PG."""

    objects = OptionManager()

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

    code = models.BigIntegerField(null=True, blank=True, verbose_name=_('code'))  # Ignore CPDBear
    mark = models.CharField(default='', max_length=500, blank=True, verbose_name=_('mark'))
    tags = models.ManyToManyField(
        'Tag',
        related_name='options',
        blank=True,
        verbose_name=_('tags'),
    )
    product = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE,
        related_name='options',
        verbose_name=_('product'),
    )
    date_price_updated = models.DateField(auto_now_add=True, verbose_name=_('date price updated'))
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
        return f'[{self.id}] {self.name}]'

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
    def filter_by_options(self, options: typing.Iterable[Option]):
        return (
            self
            .filter(options__in=options)
            .distinct()
        )

    def exclude_by_options(self, options: typing.Iterable[Option]):
        return (
            self
            .exclude(options__in=options)
            .distinct()
        )


class TagManager(models.Manager.from_queryset(TagQuerySet)):
    pass


class Tag(catalog.models.Tag):
    objects = TagManager()

    group = models.ForeignKey(
        TagGroup, on_delete=models.CASCADE, null=True, related_name='tags',
    )
