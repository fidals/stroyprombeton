"""
Context module is part of View logic in MTV abstraction.

Every class in this module inherit some refarm.catalog.context class.
It's not good style. We should use objects composition instead.
This using will becom possible after se#567 released.
"""

from functools import partial

from django import http
from django.conf import settings
from django.shortcuts import get_object_or_404

from catalog import context, typing
from images.models import Image
from pages import context as pages_context
from stroyprombeton import models as stb_models, context as stb_context, request_data


class TagsByOptions(context.Tags):

    def __init__(self, tags: context.Tags, options: stb_models.OptionQuerySet):
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
class Page(context.Context):

    def __init__(self, page, tags: context.Tags):
        self._page = page
        self._tags = tags

    def context(self) -> typing.ContextDict:
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


class Catalog(context.Context):

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

    def context(self) -> typing.ContextDict:
        tags = FilteredTags(stb_models.Tag.objects.all(), self.request_data)
        options_ = stb_context.options.Filtered(self.category, tags.qs())

        if not options_.qs():
            raise http.Http404('<h1>В категории нет изделий</h1')

        # @todo #514:60m  Create PaginatedOptions class.
        #  Without code doubling between the new class
        #  and `context.products.PaginatedProducts` one.
        sliced_options = context.products.PaginatedProducts(
            products=options_.qs(),
            url=self.request_data.request.path,
            page_number=self.request_data.pagination_page_number,
            per_page=self.request_data.pagination_per_page,
        )

        images = context.products.ProductImages(
            sliced_options.products, Image.objects.all()
        )
        grouped_tags = context.tags.GroupedTags(
            tags=TagsByOptions(stb_context.tags.All(), options_.qs())
        )
        page = Page(self.page, tags)
        category = CategoryContext(self.request_data)
        params = {
            'limits': settings.CATEGORY_STEP_MULTIPLIERS,
        }

        # @todo #419:30m  Rename 'products' template var to 'positions'
        return {
            **params,
            **pages_context.Contexts([
                page, category, sliced_options,
                images, grouped_tags
            ]).context()
        }


class CategoryContext(context.Context):

    def __init__(self, request_data_: request_data.Category):
        self.request_data = request_data_

    def object(self) -> stb_models.Category:
        return get_object_or_404(
            stb_models.Category.objects.active().prefetch_related('page'),
            id=self.request_data.id
        )

    def context(self):
        return {'category': self.object()}


class FilteredTags(context.Tags):

    def __init__(
        self,
        tags: stb_models.TagQuerySet,
        request_data_: request_data.Category
    ):
        super().__init__(qs=tags)
        self.request_data = request_data_

    def qs(self) -> stb_models.TagQuerySet:
        selected_tags = context.tags.ParsedTags(
            tags=context.Tags(self._qs),
            raw_tags=self.request_data.tags,
        )
        if self.request_data.tags:
            selected_tags = context.tags.Checked404Tags(selected_tags)
        return selected_tags.qs()


class FetchOptions(context.Context):

    # redefined just to type hint
    def __init__(self, request_data_: request_data.FetchProducts):
        self.request_data = request_data_

    def context(self) -> typing.ContextDict:
        category = CategoryContext(self.request_data)
        tags = FilteredTags(stb_models.Tag.objects.all(), self.request_data)
        options_ = stb_context.options.Sliced(
            request_data_=self.request_data,
            options=stb_context.options.Searched(
                request_data_=self.request_data,
                options=stb_context.options.Filtered(
                    category.object(), tags.qs(),
                )
            )
        )
        images = context.products.ProductImages(
            options_.qs(), Image.objects.all()
        )

        return {
            'total_products': options_.qs().count(),
            **pages_context.Contexts([options_, images]).context()
        }
