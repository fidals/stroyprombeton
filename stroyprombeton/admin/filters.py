from itertools import chain

from django.contrib import admin
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Func, Value
from django.utils.translation import ugettext_lazy as _


class ParentFilter(admin.SimpleListFilter):

    title = _('parent')
    parameter_name = 'parent'

    def lookups(self, request, model_admin):
        return (
            ('news', _('news')),
            ('regions', _('regions')),
            ('client-feedbacks', _('client feedbacks')),
        )

    def queryset(self, request, queryset):
        if not self.value():
            return

        return queryset.filter(parent__slug=self.value())


class DuplicateFilter(admin.SimpleListFilter):

    title = _('duplicates')
    parameter_name = 'duplicates'

    def lookups(self, request, model_admin):
        return (
            ('markh1', _('Mark and h1')),
            ('all', _('Mark, code, price, series and etc.'))
            # @todo #591:60m Implement duplicates filter by tags, mark and series.

            # ('params', _('Mark, series and parameters')),
        )

    def queryset(self, request, queryset):
        lookup = self.value()
        if not lookup:
            return

        def find_duplicates_by_field(queryset, field_name):
            return set(chain.from_iterable(
                queryset
                .values(field_name)
                .annotate(ids=ArrayAgg('id'))
                .annotate(c=Func('ids', Value(1), function='array_length'))
                .order_by()
                .filter(c__gt=1)
                .values_list('ids', flat=True)
            ))

        if lookup == 'markh1':
            ids = [
                find_duplicates_by_field(queryset, field_name)
                for field_name in ['product__page__name', 'mark']

            ]
            return queryset.filter(id__in=set.intersection(*ids))

        if lookup == 'all':
            ids = [
                find_duplicates_by_field(queryset, field_name)
                for field_name in [
                    'price', 'code', 'mark', 'product__page__description',
                    'product__page__title', 'product__page__name',
                    'product__page__h1',
                ]
            ]
            return queryset.filter(id__in=set.intersection(*ids))


class SpecificationFilter(admin.SimpleListFilter):

    title = _('specification')
    parameter_name = 'specification'

    def lookups(self, request, model_admin):
        return (
            ('yes', _('Has specification')),
            ('no', _('Has no specification')),
        )

    def queryset(self, request, queryset):

        if not self.value():
            return

        related_model_name = queryset.first().related_model_name
        lookup = {
            '{}__specification'.format(related_model_name): '',
        }
        without_spec = self.value() == 'no'
        return (
            queryset.filter(**lookup) if without_spec
            else queryset.exclude(**lookup)
        )
