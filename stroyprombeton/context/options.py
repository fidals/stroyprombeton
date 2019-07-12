import abc
from functools import reduce
from operator import or_

from django.conf import settings
from django.db import models
from django.shortcuts import _get_queryset

from catalog import typing
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


class Options(abc.ABC):

    @abc.abstractmethod
    def qs(self) -> stb_models.OptionQuerySet:
        ...

    def context(self) -> typing.ContextDict:
        return {
            'products': self.qs()
        }


class All(Options):

    def __init__(self, qs: stb_models.OptionQuerySet = None):
        self._qs = qs or stb_models.Option.objects.all()

    def qs(self) -> stb_models.OptionQuerySet:
        return (
            self._qs
            .bind_fields()
            .active()
            .order_by(*settings.OPTIONS_ORDERING)
        )


class CategoryFiltered(Options):

    def __init__(
        self,
        options: Options,
        category: stb_models.Category
    ):
        self.options = options
        self.category = category

    def qs(self) -> stb_models.OptionQuerySet:
        return (
            self.options
            .qs()
            .filter_descendants(self.category)
        )


class TagsFiltered(Options):
    def __init__(
        self,
        options: Options,
        tags: stb_models.TagQuerySet,
    ):
        self.options = options
        self.tags = tags

    def qs(self) -> stb_models.OptionQuerySet:
        return (
            self.options
            .qs()
            .tagged_or_all(self.tags)
        )


class Filtered(Options):
    def __init__(
        self,
        category: stb_models.Category,
        tags: stb_models.TagQuerySet,
    ):
        """Filtered options by a category and tags."""
        self.filtered = TagsFiltered(
            CategoryFiltered(
                All(),
                category,
            ),
            tags,
        )

    def qs(self) -> stb_models.OptionQuerySet:
        return self.filtered.qs()


class Searched(Options):

    LOOKUPS = [
        'product__name__icontains',
        'code__icontains',
        'mark__icontains',
    ]

    def __init__(  # Ignore CPDBear
        self,
        options: Options,
        request_data_: request_data.FetchProducts
    ):
        self.options = options
        self.request_data = request_data_

    def qs(self) -> stb_models.OptionQuerySet:
        if self.request_data.filtered and self.request_data.term:
            return search(
                self.request_data.term,
                self.options.qs(),
                self.LOOKUPS,
                ordering=('product__name', )
            )
        else:
            return self.options.qs()


class Sliced(Options):
    def __init__(
        self,
        options: Options,
        request_data_: request_data.FetchProducts
    ):
        self.options = options
        self.request_data = request_data_

    def qs(self) -> stb_models.OptionQuerySet:
        offset, limit = self.request_data.offset, self.request_data.length
        return self.options.qs()[offset:offset + limit]
