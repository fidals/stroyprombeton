from django.contrib import admin
from django.contrib.redirects.models import Redirect
from django.utils.translation import ugettext_lazy as _

from pages import models as pages_models
from generic_admin import models, inlines, sites, filters

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


class StbAdminSite(sites.SiteWithTableEditor):
    site_header = 'Stroyprombeton administration'
    table_editor_view = TableEditor


class CategoryInline(inlines.CategoryInline):
    model = stb_models.Category


class FlatPageAdmin(models.FlatPageAdmin):
    list_filter = [
        'is_active',
        filters.HasContent,
        filters.HasImages,
        ParentFilter,
    ]


class ProductInline(inlines.ProductInline):
    model = stb_models.Product
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
    category_page_model = stb_models.CategoryPage
    inlines = [ProductInline, inlines.ImageInline]


class CategoryPageAdmin(models.CategoryPageAdmin):
    inlines = [CategoryInline, inlines.ImageInline]


stb_admin_site = StbAdminSite(name='stb_admin')

# Pages
stb_admin_site.register(pages_models.CustomPage, models.CustomPageAdmin)
stb_admin_site.register(pages_models.FlatPage, FlatPageAdmin)

# STB
stb_admin_site.register(stb_models.ProductPage, ProductPageAdmin)
stb_admin_site.register(stb_models.CategoryPage, CategoryPageAdmin)
stb_admin_site.register(stb_models.NewsForAdmin, FlatPageAdmin)
stb_admin_site.register(stb_models.RegionsForAdmin, FlatPageAdmin)
stb_admin_site.register(stb_models.ClientFeedbacksForAdmin, FlatPageAdmin)

# Redirects
stb_admin_site.register(Redirect)
