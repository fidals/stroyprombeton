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


class CharacteristicsEqualityFilter(admin.SimpleListFilter):

    title = _('characteristics equality')
    parameter_name = 'equality'

    def lookups(self, request, model_admin):
        return (
            ('h1', _('Only same h1')),
            ('all', _('Same h1, characteristics, price'))
        )

    def queryset(self, request, queryset):
        if not self.value():
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

        if self.value() == 'h1':
            ids = [
                find_duplicates_by_field(queryset, field_name)
                for field_name in ['name', 'stroyprombeton_product__mark']
            ]
            return queryset.filter(id__in=set.intersection(*ids))

        if self.value() == 'all':
            ids = [
                find_duplicates_by_field(queryset, field_name)
                for field_name in [
                    'stroyprombeton_product__price', 'stroyprombeton_product__code',
                    'stroyprombeton_product__mark', 'stroyprombeton_product__specification',
                    'stroyprombeton_product__length', 'stroyprombeton_product__width',
                    'stroyprombeton_product__height', 'stroyprombeton_product__weight',
                    'stroyprombeton_product__volume', 'stroyprombeton_product__diameter_out',
                    'stroyprombeton_product__diameter_in', 'description', 'title', 'name', 'h1'
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
