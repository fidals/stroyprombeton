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
