"""
Context module is part of View logic in MTV abstraction.

Every class in this module inherit some refarm.catalog.context class.
It's not good style. We should use objects composition instead.
This using will becom possible after se#567 released.
"""

import typing
from functools import partial, reduce
from operator import or_

from django.conf import settings
from django.db import models
from django.shortcuts import get_object_or_404, _get_queryset

from catalog import newcontext
from images.models import Image
from pages import newcontext as pages_newcontext
from search.search import QuerySetType
from stroyprombeton import models as stb_models, request_data


# doubled `search.search.search` here to change name to product__name.
# Redesign search module on refarm side in more extensible way.
def search(term: str, model_type: typing.Union[models.Model, models.Manager, QuerySetType],
           lookups: list, ordering) -> QuerySetType:
    """Return search results based on a given model."""
    def _get_Q(lookup):
        return models.Q(**{lookup: term})

    term = term.strip()
    query_set = _get_queryset(model_type)
    query = reduce(or_, map(_get_Q, lookups))

    return (
        query_set.filter(query)
        .annotate(
            is_name_start_by_term=models.Case(models.When(
                product__name__istartswith=term,
                then=models.Value(True)),
                default=models.Value(False),
                output_field=models.BooleanField()
            )
        )
        .order_by(models.F('is_name_start_by_term').desc(), *ordering)
    )


class TagsByOptions(newcontext.Tags):

    def __init__(self, tags: newcontext.Tags, options: stb_models.OptionQuerySet):
        self._tags = tags
        self.options = options

    def qs(self):
        return (
            self._tags.qs()
            .filter(options__in=self.options)
            .order_by_alphanumeric()
            .distinct()
        )


# @todo #431:30m  Share base page to refarm side. se2
class Page(newcontext.Context):

    def __init__(self, page, tags: newcontext.Tags):
        self._page = page
        self._tags = tags

    def context(self):
        def template_context(page, tag_titles, tags):
            return {
                'page': page,
                'tag_titles': tag_titles,
                'tags': tags,
            }

        tags_qs = self._tags.qs()
        self._page.get_template_render_context = partial(
            template_context, self._page, tags_qs.as_title(), tags_qs
        )

        return {
            'page': self._page,
        }


# @todo #443:60m  Improve context classes arch.
#  Move `Catalog.select_tags` and `Catalog.filter_products` to some common area.
#  Reuse the methods at pretty separated `Catalog` and `FetchProducts` classes.
#  Move `sliced_products` inside of `context` method for both classes.
#  Move `FetchProducts.filter_` and `FetchProducts.LOOKUPS` to some search entity.
class Catalog(newcontext.Context):

    def __init__(self, request_data_: request_data.Category):
        self.request_data = request_data_

    @property
    def page(self):
        return self.category.page

    @property
    def category(self):
        return get_object_or_404(
            stb_models.Category.objects.active().prefetch_related('page'),
            id=self.request_data.id
        )

    @property
    def tags(self) -> newcontext.Tags:
        return newcontext.Tags(stb_models.Tag.objects.all())

    def select_tags(self) -> newcontext.Tags:
        all_tags = self.tags

        selected_tags = newcontext.tags.ParsedTags(
            tags=all_tags,
            raw_tags=self.request_data.tags,
        )
        if self.request_data.tags:
            selected_tags = newcontext.tags.Checked404Tags(selected_tags)
        return selected_tags

    def filter_positions(self) -> stb_models.OptionQuerySet:
        products = (
            stb_models.Product.objects.active()
            .bind_fields()
            .filter_descendants(self.category)
            .tagged_or_all(self.select_tags().qs())
            .order_by(*settings.PRODUCTS_ORDERING)
        )
        # @todo #419:30m  Fetch options and products with one query.
        return (
            stb_models.Option.objects
            .bind_fields()
            .filter(product__in=products)
        )

    def slice_products(self) -> newcontext.products.PaginatedProducts:
        """
        We have to use separated variable/method for pagination.

        Because paginated QuerySet can not used as QuerySet.
        It's not the most strong place of Django ORM, of course.
        :return: ProductsContext with paginated QuerySet inside
        """
        return newcontext.products.PaginatedProducts(
            products=self.filter_positions(),
            url=self.request_data.request.path,
            page_number=self.request_data.pagination_page_number,
            per_page=self.request_data.pagination_per_page,
        )

    # @todo #443:15m  Create ContextDict type on refarm side. se2
    def context(self) -> dict:
        selected_tags = self.select_tags()
        products = self.filter_positions()
        sliced_products = self.slice_products()

        images = newcontext.products.ProductImages(sliced_products.products, Image.objects.all())
        grouped_tags = newcontext.tags.GroupedTags(
            tags=TagsByOptions(self.tags, products)
        )
        page = Page(self.page, selected_tags)
        category = newcontext.category.Context(self.category)
        params = {
            'limits': settings.CATEGORY_STEP_MULTIPLIERS,
        }

        # @todo #419:30m  Rename 'products' template var to 'positions'
        return {
            **params,
            # @todo #431:60m  Move total_products to a relevant context class.
            #  At SE side "paginated" context var somehow contains "total_products" field.
            #  And move the relevant `test_tag_button_filter_products` test to the fast tests side.
            'total_products': products.count(),
            **pages_newcontext.Contexts([
                page, category, sliced_products,
                images, grouped_tags
            ]).context()
        }


class FetchPositions(Catalog):

    LOOKUPS = [
        'product__name__icontains',
        'code__icontains',
        'mark__icontains',
    ]

    # redefined just to type hint
    def __init__(self, request_data_: request_data.FetchProducts):
        super().__init__(request_data_)

    def filter_positions(self) -> stb_models.OptionQuerySet:
        products = super().filter_positions()

        if self.request_data.filtered and self.request_data.term:
            return search(
                self.request_data.term,
                products,
                self.LOOKUPS,
                ordering=('product__name', )
            )
        else:
            return products

    def slice_products(self):
        offset, limit = self.request_data.offset, self.request_data.length
        return newcontext.Products(
            self.filter_positions()[offset:offset + limit]
        )
