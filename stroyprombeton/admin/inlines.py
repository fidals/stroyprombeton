from django.contrib import admin
from django_select2.forms import ModelSelect2Widget

from ecommerce.models import Position
from generic_admin import inlines

from stroyprombeton import models as stb_models
from stroyprombeton.forms import AdminWidgetsForm


class PositionInline(admin.StackedInline):

    model = Position


class ImageInline(inlines.ImageInline):

    form = AdminWidgetsForm


class CategoryInline(inlines.CategoryInline):

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
        if db_field.name == 'parent':  # Ignore CPDBear
            kwargs['widget'] = ModelSelect2Widget(
                model=stb_models.Category,
                search_fields=[
                    'name__icontains',
                    'pk__startswith',
                ],
            )
        return super().formfield_for_dbfield(db_field, **kwargs)


class ProductInline(inlines.ProductInline):

    model = stb_models.Product
    form = AdminWidgetsForm
    fieldsets = ((None, {
        'classes': ('primary-chars', ),
        'fields': (
            ('name', 'id'),
            ('category', 'correct_category_id'),
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
        return super().formfield_for_dbfield(db_field, **kwargs)


class SeriesInline(admin.StackedInline):

    model = stb_models.Series
