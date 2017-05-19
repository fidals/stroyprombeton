from django import forms
from django.contrib import admin
from django.contrib.redirects.models import Redirect
from django.utils.translation import ugettext_lazy as _

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


class StbProductPageAdmin(admin_models.ProductPageAdmin):
    form = CustomWidgetsForm
    category_page_model = stb_models.CategoryPage
    inlines = [StbProductInline, StbImageInline]


class StbCategoryPageAdmin(admin_models.CategoryPageAdmin):
    form = CustomWidgetsForm
    inlines = [StbCategoryInline, StbImageInline]


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
