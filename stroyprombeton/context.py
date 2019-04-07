"""
Context module is part of View logic in MTV abstraction.

Every class in this module inherit some refarm.catalog.context class.
It's not good style. We should use objects composition instead.
This using will becom possible after se#567 released.
"""

from functools import partial, reduce
from operator import or_

from django.conf import settings
from django.db import models
from django.shortcuts import get_object_or_404, _get_queryset

from catalog import context, typing
from images.models import Image
from pages import context as pages_context
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

    @property
    def tags(self) -> context.Tags:
        return context.Tags(stb_models.Tag.objects.all())

    def context(self) -> typing.ContextDict:
        tags = FilteredTags(stb_models.Tag.objects.all(), self.request_data)
        options = FilteredOptions(self.category, tags.qs(), self.request_data)

        # @todo #514:60m  Create PaginatedOptions class.
        #  Without code doubling between the new class
        #  and `context.products.PaginatedProducts` one.
        sliced_options = context.products.PaginatedProducts(
            products=options.qs(),
            url=self.request_data.request.path,
            page_number=self.request_data.pagination_page_number,
            per_page=self.request_data.pagination_per_page,
        )

        images = context.products.ProductImages(
            sliced_options.products, Image.objects.all()
        )
        grouped_tags = context.tags.GroupedTags(
            tags=TagsByOptions(self.tags, options.qs())
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


# @todo #514:30m  Improve Options contexts structure.
#  Move all Options context classes to separated module.
#  And create base class for them to remove code doubling.
class FilteredOptions(context.Context):
    def __init__(
        self,
        category: stb_models.Category,
        tags: stb_models.TagQuerySet,
        request_data_: request_data.Category
    ):
        self.category = category
        self.tags = tags
        self.request_data = request_data_

    def qs(self) -> stb_models.OptionQuerySet:
        return (
            stb_models.Option.objects
            .bind_fields()
            .active()
            .filter_descendants(self.category)
            .tagged_or_all(self.tags)
            .order_by(*settings.OPTIONS_ORDERING)
        )

    def context(self) -> typing.ContextDict:
        return {
            'positions': self.qs()
        }


class SearchedOptions(context.Context):

    LOOKUPS = [
        'product__name__icontains',
        'code__icontains',
        'mark__icontains',
    ]

    def __init__(  # Ignore CPDBear
        self,
        options: stb_models.OptionQuerySet,
        request_data_: request_data.FetchProducts
    ):
        self.options = options
        self.request_data = request_data_

    def qs(self) -> stb_models.OptionQuerySet:
        if self.request_data.filtered and self.request_data.term:
            return search(
                self.request_data.term,
                self.options,
                self.LOOKUPS,
                ordering=('product__name', )
            )
        else:
            return self.options

    def context(self) -> typing.ContextDict:
        return {
            'positions': self.qs()
        }


class SlicedOptions(context.Context):
    def __init__(
        self,
        options: stb_models.OptionQuerySet,
        request_data_: request_data.FetchProducts
    ):
        self.options = options
        self.request_data = request_data_

    def qs(self) -> stb_models.OptionQuerySet:
        offset, limit = self.request_data.offset, self.request_data.length
        return self.options[offset:offset + limit]

    def context(self) -> typing.ContextDict:
        return {
            'products': self.qs()
        }


class FetchPositions(context.Context):

    # redefined just to type hint
    def __init__(self, request_data_: request_data.FetchProducts):
        self.request_data = request_data_

    def context(self) -> typing.ContextDict:
        category = CategoryContext(self.request_data)
        tags = FilteredTags(stb_models.Tag.objects.all(), self.request_data)
        # @todo #514:30m  Pass Context objects inside every context class.
        #  Every class in the current module.
        #  should receive `Context` object as `options` arg,
        #  Now they receive `OptionsQuerySet` objects.
        options = SlicedOptions(
            request_data_=self.request_data,
            options=SearchedOptions(
                request_data_=self.request_data,
                options=FilteredOptions(
                    category.object(), tags.qs(), self.request_data
                ).qs()
            ).qs()
        )
        images = context.products.ProductImages(
            options.qs(), Image.objects.all()
        )

        return {
            'total_products': options.qs().count(),
            **pages_context.Contexts([options, images]).context()
        }
