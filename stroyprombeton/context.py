"""
Context module is part of View logic in MTV abstraction.

Every class in this module inherit some refarm.catalog.context class.
It's not good style. We should use objects composition instead.
This using will becom possible after se#567 released.
"""

import typing
from functools import lru_cache, partial

from django.conf import settings
from django.shortcuts import get_object_or_404

from catalog import context, newcontext
from catalog.models import ProductQuerySet
from images.models import Image
from pages import newcontext as pages_newcontext, models as pages_models
from stroyprombeton import models, request_data


class Category(context.Category):
    pk_url_kwarg = 'category_id'

    @property
    @lru_cache(maxsize=1)
    def page(self):
        model_name = models.Category().related_model_name
        lookup = f'{model_name}__id'
        category_pk = self.url_kwargs.get('category_id')
        return (
            pages_models.ModelPage.objects
            .prefetch_related(model_name)
            .filter(**{lookup: category_pk})
            .get()
        )


class SortingCategory(context.SortingCategory):

    @property
    @lru_cache(maxsize=1)
    def page(self):
        return self.super.page

    def get_sorting_options(self) -> typing.List[str]:
        return settings.PRODUCTS_ORDERING


class TaggedCategory(context.TaggedCategory):
    @property
    @lru_cache(maxsize=1)
    def page(self):
        return self.super.page

    def get_undirected_sorting_options(self) -> typing.List[str]:
        return settings.PRODUCTS_ORDERING


class ProductImages(context.AbstractProductsListContext):

    @property
    def product_pages(self):
        return models.ProductPage.objects.all()

    @property
    def images(self) -> typing.Dict[int, Image]:
        assert isinstance(self.products, ProductQuerySet)

        images = {}
        if self.product_pages:
            images = Image.objects.get_main_images_by_pages(
                self.product_pages.filter(stroyprombeton_product__in=self.products)
            )

        return {
            product.id: images.get(product.page)
            for product in self.products
        }

    def get_context_data(self):
        return {
            'product_images': self.images,
            **(
                self.super.get_context_data()
                if self.super else {}
            ),
        }


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


class Catalog(newcontext.Context):
    PRODUCTS_ON_PAGE_PC = 48
    PRODUCTS_ON_PAGE_MOB = 12

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

    # @todo #431:15m  Create type hints for context on refarm side. se2
    def context(self) -> dict:
        all_tags = newcontext.Tags(models.Tag.objects.all())

        selected_tags = newcontext.tags.ParsedTags(
            tags=all_tags,
            raw_tags=self.request_data.tags,
        )
        if self.request_data.tags:
            selected_tags = newcontext.tags.Checked404Tags(selected_tags)

        products = (
            models.Product.objects.active()
            .bind_fields()
            .filter_descendants(self.category)
            .tagged_or_all(selected_tags.qs())
            .order_by(*settings.PRODUCTS_ORDERING)
        )

        """
        We have to use separated variable for pagination.

        Because paginated QuerySet can not used as QuerySet.
        It's not the most strong place of Django ORM, of course.
        :return: ProductsContext with paginated QuerySet inside
        """
        paginated = newcontext.products.PaginatedProducts(
            products=products,
            url=self.request_data.request.path,
            page_number=self.request_data.pagination_page_number,
            per_page=self.request_data.pagination_per_page,
        )

        images = newcontext.products.ProductImages(paginated.products, Image.objects.all())
        brands = newcontext.products.ProductBrands(paginated.products, all_tags)
        grouped_tags = newcontext.tags.GroupedTags(
            tags=newcontext.tags.TagsByProducts(all_tags, products)
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
                page, category, paginated,
                images, brands, grouped_tags
            ]).context()
        }
