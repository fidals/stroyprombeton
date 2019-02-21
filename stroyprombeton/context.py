"""
Context module is part of View logic in MTV abstraction.

Every class in this module inherit some refarm.catalog.context class.
It's not good style. We should use objects composition instead.
This using will becom possible after se#567 released.
"""

from functools import partial

from django.conf import settings
from django.shortcuts import get_object_or_404

from catalog import newcontext
from catalog.models import ProductQuerySet
from images.models import Image
from pages import newcontext as pages_newcontext
from search.search import search as filter_
from stroyprombeton import models, request_data


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
            models.Category.objects.active().prefetch_related('page'),
            id=self.request_data.id
        )

    @property
    def tags(self) -> newcontext.Tags:
        return newcontext.Tags(models.Tag.objects.all())

    def select_tags(self) -> newcontext.Tags:
        all_tags = self.tags

        selected_tags = newcontext.tags.ParsedTags(
            tags=all_tags,
            raw_tags=self.request_data.tags,
        )
        if self.request_data.tags:
            selected_tags = newcontext.tags.Checked404Tags(selected_tags)
        return selected_tags

    def filter_products(self) -> ProductQuerySet:
        return (
            models.Product.objects.active()
            .bind_fields()
            .filter_descendants(self.category)
            .tagged_or_all(self.select_tags().qs())
            .order_by(*settings.PRODUCTS_ORDERING)
        )

    def slice_products(self) -> newcontext.products.PaginatedProducts:
        """
        We have to use separated variable/method for pagination.

        Because paginated QuerySet can not used as QuerySet.
        It's not the most strong place of Django ORM, of course.
        :return: ProductsContext with paginated QuerySet inside
        """
        return newcontext.products.PaginatedProducts(
            products=self.filter_products(),
            url=self.request_data.request.path,
            page_number=self.request_data.pagination_page_number,
            per_page=self.request_data.pagination_per_page,
        )

    # @todo #443:15m  Create ContextDict type on refarm side. se2
    def context(self) -> dict:
        selected_tags = self.select_tags()
        products = self.filter_products()
        sliced_products = self.slice_products()

        images = newcontext.products.ProductImages(sliced_products.products, Image.objects.all())
        grouped_tags = newcontext.tags.GroupedTags(
            tags=newcontext.tags.TagsByProducts(self.tags, products)
        )
        page = Page(self.page, selected_tags)
        category = newcontext.category.Context(self.category)
        params = {
            'limits': settings.CATEGORY_STEP_MULTIPLIERS,
        }

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


class FetchProducts(Catalog):

    LOOKUPS = [
        'name__icontains',
        'code__icontains',
        'mark__icontains',
        'specification__icontains',
    ]

    # redefined just to type hint
    def __init__(self, request_data_: request_data.FetchProducts):
        super().__init__(request_data_)

    def filter_products(self) -> ProductQuerySet:
        products = super().filter_products()

        if self.request_data.filtered and self.request_data.term:
            return filter_(
                self.request_data.term,
                products,
                self.LOOKUPS,
            )
        else:
            return products

    def slice_products(self):
        offset, limit = self.request_data.offset, self.request_data.length
        return newcontext.Products(
            self.filter_products()[offset:offset + limit]
        )
