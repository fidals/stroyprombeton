from itertools import chain

from django import forms
from django.contrib import admin
from django.contrib.postgres.aggregates import ArrayAgg
from django.contrib.redirects.models import Redirect
from django.db.models import Func, Value
from django.utils.translation import ugettext_lazy as _
from django_select2.forms import ModelSelect2Widget

from pages import models as pages_models
from generic_admin import models as admin_models, inlines, sites, filters

from stroyprombeton import models as stb_models
from stroyprombeton.views import TableEditor


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


class CustomWidgetsForm(forms.ModelForm):
    class Meta:
        widgets = {
            'description': forms.TextInput,
            'seo_text': forms.TextInput,
            'specification': forms.TextInput,
            'title': forms.TextInput,
        }
        fields = '__all__'


class StbAdminSite(sites.SiteWithTableEditor):
    site_header = _('Stroyprombeton administration')
    table_editor_view = TableEditor


class StbImageInline(inlines.ImageInline):
    form = CustomWidgetsForm


class StbCategoryInline(inlines.CategoryInline):
    model = stb_models.Category

    fieldsets = ((None, {
        'classes': ('primary-chars', ),
        'fields': (
            ('name', 'id'),
            ('parent', 'correct_parent_id'),
            ('specification', ),
        )
    }),)

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'parent':
            kwargs['widget'] = ModelSelect2Widget(
                model=stb_models.Category,
                search_fields=[
                    'name__icontains',
                    'pk__startswith',
                ],
            )
        return super(StbCategoryInline, self).formfield_for_dbfield(
            db_field,
            **kwargs,
        )


class StbCustomPageAdmin(admin_models.CustomPageAdmin):
    form = CustomWidgetsForm
    inlines = [StbImageInline]


class StbFlatPageAdmin(admin_models.FlatPageAdmin):
    form = CustomWidgetsForm
    inlines = [StbImageInline]
    list_filter = [
        'is_active',
        filters.HasContent,
        filters.HasImages,
        ParentFilter,
    ]


class StbProductInline(inlines.ProductInline):
    model = stb_models.Product
    form = CustomWidgetsForm
    fieldsets = ((None, {
        'classes': ('primary-chars', ),
        'fields': (
            ('name', 'id'),
            ('category', 'correct_category_id'),
            ('price', 'is_new_price'),
            ('in_stock', 'is_popular'),
            ('code', 'mark'),
            'specification',
            ('length', 'width'),
            ('height', 'weight'),
            ('diameter_out', 'diameter_in'),
            'volume',
        )
    }),)

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'category':
            kwargs['widget'] = ModelSelect2Widget(
                model=stb_models.Category,
                search_fields=[
                    'name__icontains',
                    'pk__startswith',
                ],
            )
        return super(StbProductInline, self).formfield_for_dbfield(
            db_field,
            **kwargs,
        )


class StbProductPageAdmin(admin_models.ProductPageAdmin):
    form = CustomWidgetsForm
    category_page_model = stb_models.CategoryPage
    inlines = [StbProductInline, StbImageInline]
    list_filter = [
        'is_active',
        filters.PriceRange,
        filters.HasContent,
        filters.HasImages,
        CharacteristicsEqualityFilter,
    ]


class StbCategoryPageAdmin(admin_models.CategoryPageAdmin):
    form = CustomWidgetsForm
    inlines = [StbCategoryInline, StbImageInline]
    list_filter = [
        'is_active',
        filters.HasContent,
        filters.HasImages,
        SpecificationFilter,
    ]


stb_admin_site = StbAdminSite(name='stb_admin')

# Pages
stb_admin_site.register(pages_models.PageTemplate, admin_models.CustomPageTemplateAdmin)
stb_admin_site.register(pages_models.CustomPage, StbCustomPageAdmin)
stb_admin_site.register(pages_models.FlatPage, StbFlatPageAdmin)

# STB
stb_admin_site.register(stb_models.ProductPage, StbProductPageAdmin)
stb_admin_site.register(stb_models.CategoryPage, StbCategoryPageAdmin)
stb_admin_site.register(stb_models.NewsForAdmin, StbFlatPageAdmin)
stb_admin_site.register(stb_models.RegionsForAdmin, StbFlatPageAdmin)
stb_admin_site.register(stb_models.ClientFeedbacksForAdmin, StbFlatPageAdmin)

# Redirects
stb_admin_site.register(Redirect)
