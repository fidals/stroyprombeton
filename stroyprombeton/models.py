import string
import typing

import mptt
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _
from unidecode import unidecode

import catalog
import ecommerce
import pages


class Order(ecommerce.models.Order):
    company = models.CharField(max_length=255, verbose_name='company')
    address = models.TextField(default='', blank=True, verbose_name='address')
    comment = models.TextField(default='', blank=True, verbose_name='comment')

    def set_positions(self, cart):
        self.save()
        for id_, position in cart:
            self.positions.create(
                order=self,
                product_id=id_,
                name=position['name'],
                price=position['price'],
                quantity=position['quantity'],
                code=position['code'],
                catalog_name=position['catalog_name'],
                url=position['url'],
            )
        return self


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

    @property
    def catalog_name(self):
        return self.name

    @classmethod
    def get_default_parent(cls):
        return pages.models.CustomPage.objects.filter(slug='gbi').first()

    def get_absolute_url(self):
        """Return url for model."""
        return reverse('category', args=(self.id,))

    def get_series(self) -> models.QuerySet:
        return (
            Series.objects
            .prefetch_related('options')
            .filter(
                options__in=models.Subquery(
                    Option.objects
                    .select_related('product')
                    .select_related('product__category')
                    .filter(
                        product__in=Product.objects.filter_descendants(self)
                    ).values('id')
                )
            ).distinct()
            .order_by('name')
        )

    def recursive_products(self) -> 'ProductQuerySet':
        return Product.objects.filter_descendants(self)

    def get_min_price(self) -> float:
        """Helper for templates."""
        return self.recursive_products().options().min_price()


class SeriesQuerySet(models.QuerySet):

    def bind_fields(self):
        """Prefetch or select typical related fields to reduce sql queries count."""
        return self.select_related('page')  # Ignore CPDBear

    def active(self) -> 'SeriesQuerySet':
        return self.filter(page__is_active=True)

    def exclude_empty(self) -> 'SeriesQuerySet':
        return (
            self.active()
            .filter(options__product__page__is_active=True)
            .distinct()
        )


class SeriesManager(models.Manager.from_queryset(SeriesQuerySet)):
    """Get all products of given category by Category's id or instance."""

    def active(self):
        return self.get_queryset().active()


class Series(pages.models.PageMixin):
    """
    Series is another way to organize products.

    It's like Category, but has no hierarchy.
    """

    objects = SeriesManager()

    SLUG_HASH_SIZE = 5
    SLUG_MAX_LENGTH = 50

    class Meta:
        verbose_name = _('Series')
        verbose_name_plural = _('Series')  # Ignore CPDBear

    name = models.CharField(
        max_length=1000, db_index=True, unique=True, verbose_name=_('name')
    )

    @property
    def url(self):
        return self.get_absolute_url()

    def get_absolute_url(self):
        """Url path to the related page."""
        return reverse('series', args=(self.slug,))  # Ignore CPDBear

    # @todo #669:60m  Remove `Series.slug` field.
    #  Series page already contains it.
    slug = models.SlugField(
        blank=False, unique=True, max_length=SLUG_MAX_LENGTH,
    )

    # @todo #569:120m  Design unified slug autogenerating mech.
    #  Now it's doubled here and in several places at catalog.models.
    def _get_slug(self) -> str:
        # Translate all punctuation chars to "_".
        # It doesn't conflict with `slugify`, which translate spaces to "-"
        # and punctuation chars to "".
        slug = slugify(unidecode(self.name.translate(
            {ord(p): '_' for p in string.punctuation}
        )))

        # Keep the slug length less then SLUG_MAX_LENGTH
        if len(slug) < self.SLUG_MAX_LENGTH:
            return slug

        slug_length = self.SLUG_MAX_LENGTH - self.SLUG_HASH_SIZE - 1
        return catalog.models.randomize_slug(
            slug=slug[:slug_length],
            hash_size=self.SLUG_HASH_SIZE
        )

    def get_min_price(self) -> float:
        """Helper for templates."""
        return self.options.min_price()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._get_slug()
        super().save(*args, **kwargs)


class SectionQuerySet(models.QuerySet):

    def bind_fields(self):
        """Prefetch or select typical related fields to reduce sql queries count."""
        return (
            self.select_related('page')
            .prefetch_related('products')
        )

    def active(self) -> 'SeriesQuerySet':
        return self.filter(page__is_active=True)

    def exclude_empty(self) -> 'SeriesQuerySet':
        return (
            self.active()
            .filter(products__page__is_active=True)
            .distinct()
        )


class SectionManager(models.Manager.from_queryset(SeriesQuerySet)):
    """Get all products of given category by Category's id or instance."""

    def active(self):
        return self.get_queryset().active()


# @todo #669:30m  Get rid of Category-Series-Section models code doubling.
class Section(pages.models.PageMixin):
    """
    Group of products created by product type principle.

    See doc/section.md for details.
    """

    # @todo #669:30m  Doc section concept.
    #  What problem it solves, who required it.
    #  Why we solved problem in this way.

    objects = SeriesManager()

    SLUG_HASH_SIZE = 5
    SLUG_MAX_LENGTH = 50

    class Meta:
        verbose_name = _('Section')
        verbose_name_plural = _('Sections')

    name = models.CharField(
        max_length=1000, db_index=True, unique=True, verbose_name=_('name')
    )

    @property
    def url(self):
        return self.get_absolute_url()

    def get_absolute_url(self):
        """Url path to the related page."""
        return reverse('section', args=(self.page.slug,))

    def get_min_price(self) -> float:
        """Helper for templates."""
        return self.products.options().min_price()


class OptionQuerySet(models.QuerySet):

    def active(self):
        return self.filter(product__isnull=False, product__page__is_active=True)

    def bind_fields(self):
        """Prefetch or select typical related fields to reduce sql queries count."""
        return (
            self.select_related('product')
            .select_related('series')
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

    def min_price(self) -> float:
        min_price = self.aggregate(min_price=models.Min('price'))['min_price']
        return min_price or 0.0


class OptionManager(models.Manager.from_queryset(OptionQuerySet)):
    """Get all products of given category by Category's id or instance."""


class Option(catalog.models.AbstractOption):
    """This doc page describes what is option: https://goo.gl/S4U9PG."""

    class Meta:
        # Product and Option has the same verbose names
        # in case of "ЖБИ" domain area.
        verbose_name = _('Product')
        verbose_name_plural = _('Products')

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
    series = models.ForeignKey(
        Series,
        on_delete=models.CASCADE,
        related_name='options',
        verbose_name=_('series'),
        null=True,
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

    @property
    def catalog_name(self) -> str:
        return f'{self.name} {self.mark}'

    def __str__(self):
        return self.mark  # Ignore CPDBear


class ProductQuerySet(catalog.models.ProductQuerySet):

    # @todo #597:60m  Implement `ProductQuerySet.get_series` method.
    #  Then reuse it at existing `Product.get_series` method.
    #  Use this ProductQuerySet class as Product queryset.
    def get_series(self):
        pass

    def options(self) -> OptionQuerySet:
        return Option.objects.filter(product__in=self).distinct()


class ProductManager(models.Manager.from_queryset(ProductQuerySet)):
    """Get all products of given category by Category's id or instance."""

    def filter_descendants(self, category: Category) -> ProductQuerySet:
        return self.get_queryset().filter_descendants(category)

    def active(self):
        return self.get_queryset().active()

    def tagged(self, tags: typing.Iterable['Tag']):
        return self.get_queryset().tagged(tags)


# not inherited from `catalog.models.AbstractProduct`, because
# AbstractProduct's set of fields is shared between Product and Option models.
class Product(catalog.models.AbstractProduct, pages.models.PageMixin):
    objects = ProductManager()

    name = models.CharField(max_length=255, db_index=True, verbose_name=_('name'))
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name=_('category'),
    )

    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name=_('section'),
        null=True,
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

    def get_series(self) -> models.QuerySet:
        """
        Use it only for a single product.

        It'll produce N queries for a batch QuerySet with N products.
        Use ProductQS.
        """
        product = Product.objects.prefetch_related('options').get(id=self.id)
        return (
            Series.objects
            .filter(options__in=product.options.active())
            .distinct()
        )

    # @todo #597:30m  Remove Product.price field

    # we'll remove this field
    # after integration admin to Options feature at #433
    price = models.FloatField(
        blank=True,
        default=0,
        db_index=True,
        verbose_name=_('price'),
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


class SeriesPage(pages.models.ModelPage):
    """Proxy model for Admin."""

    class Meta(pages.models.ModelPage.Meta):
        proxy = True
        verbose_name = _('serie')
        verbose_name_plural = _('series')

    objects = pages.models.ModelPage.create_model_page_managers(Series)


class SectionPage(pages.models.ModelPage):
    """Proxy model for Admin."""

    class Meta(pages.models.ModelPage.Meta):
        proxy = True
        verbose_name = _('section')
        verbose_name_plural = _('sections')

    objects = pages.models.ModelPage.create_model_page_managers(Section)


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
