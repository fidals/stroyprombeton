from django.contrib import admin
from django.contrib.redirects.models import Redirect
from django.utils.translation import ugettext_lazy as _

from pages.models import CustomPage, FlatPage
from generic_admin import models, inlines, sites, filters

from stroyprombeton.models import ProductPage, CategoryPage, Category, Product
from stroyprombeton.views import TableEditor


class PageParent(admin.SimpleListFilter):
    """https://goo.gl/IYojpl"""
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


class StbAdminSite(sites.SiteWithTableEditor):
    site_header = 'Stroyprombeton administration'
    table_editor_view = TableEditor


class CategoryInline(inlines.CategoryInline):
    model = Category


class FlatPageAdmin(models.FlatPageAdmin):
    list_filter = [
        'is_active',
        filters.HasContent,
        filters.HasImages,
        PageParent,
    ]


class ProductInline(inlines.ProductInline):
    model = Product
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


class ProductPageAdmin(models.ProductPageAdmin):
    category_page_model = CategoryPage
    inlines = [ProductInline, inlines.ImageInline]


class CategoryPageAdmin(models.CategoryPageAdmin):
    inlines = [CategoryInline, inlines.ImageInline]


stb_admin_site = StbAdminSite(name='stb_admin')

stb_admin_site.register(CustomPage, models.CustomPageAdmin)
stb_admin_site.register(FlatPage, FlatPageAdmin)
stb_admin_site.register(ProductPage, ProductPageAdmin)
stb_admin_site.register(CategoryPage, CategoryPageAdmin)
stb_admin_site.register(Redirect)
