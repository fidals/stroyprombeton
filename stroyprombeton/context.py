"""
Context module is part of View logic in MTV abstraction.

Every class in this module inherit some refarm.catalog.context class.
It's not good style. We should use objects composition instead.
This using will becom possible after se#567 released.
"""

from functools import lru_cache
import typing

from django.conf import settings

from catalog import context
from catalog.models import ProductQuerySet
from images.models import Image
from pages.models import ModelPage

from stroyprombeton import models as stb_models


class Category(context.Category):
    pk_url_kwarg = 'category_id'

    @property
    @lru_cache(maxsize=1)
    def page(self):
        model_name = stb_models.Category().related_model_name
        lookup = f'{model_name}__id'
        category_pk = self.url_kwargs.get(self.pk_url_kwarg)
        return (
            ModelPage.objects
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
        return stb_models.ProductPage.objects.all()

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
