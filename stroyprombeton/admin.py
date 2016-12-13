from django.contrib.redirects.models import Redirect

from pages.models import CustomPage, FlatPage
from generic_admin import models, inlines, sites

from stroyprombeton.models import ProductPage, CategoryPage, Category, Product
from stroyprombeton.views import TableEditor


class StbAdminSite(sites.SiteWithTableEditor):
    site_header = 'Stroyprombeton administration'
    table_editor_view = TableEditor


class CategoryInline(inlines.CategoryInline):
    model = Category


class ProductInline(inlines.ProductInline):
    model = Product
    fieldsets = ((None, {
        'classes': ('primary-chars', ),
        'fields': (
            ('name', 'id'),
            ('category', 'correct_category_id'),
            ('price', 'is_new_price',),
            ('in_stock', 'is_popular'),
            ('code', 'mark'),
            'specification',
            ('length', 'width', 'height', 'weight', 'volume', 'diameter_out', 'diameter_in')
        )
    }),)


class ProductPageAdmin(models.ProductPageAdmin):
    category_page_model = CategoryPage
    inlines = [ProductInline, inlines.ImageInline]


class CategoryPageAdmin(models.CategoryPageAdmin):
    inlines = [CategoryInline, inlines.ImageInline]


stb_admin_site = StbAdminSite(name='stb_admin')

stb_admin_site.register(CustomPage, models.CustomPageAdmin)
stb_admin_site.register(FlatPage, models.FlatPageAdmin)
stb_admin_site.register(ProductPage, ProductPageAdmin)
stb_admin_site.register(CategoryPage, CategoryPageAdmin)
stb_admin_site.register(Redirect)
