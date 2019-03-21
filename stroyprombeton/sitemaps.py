from django.conf import settings
from django.contrib.sitemaps import Sitemap

from pages.models import CustomPage, FlatPage, ModelPage

# @todo #396:60m Adapt sitemaps for Option model.


class AbstractSitemap(Sitemap):
    protocol = settings.PROTOCOL
    changefreq = 'weekly'
    priority = 0.9


class IndexSitemap(Sitemap):
    protocol = settings.PROTOCOL
    changefreq = 'monthly'
    priority = 1

    def items(self):
        return CustomPage.objects.filter(slug='')


class FlatPagesSitemap(AbstractSitemap):

    def items(self):
        return FlatPage.objects.active()


class CustomPagesSitemap(AbstractSitemap):

    def items(self):
        return CustomPage.objects.active().exclude(slug='')


class ProductPagesSitemap(AbstractSitemap):

    def items(self):
        return (
            ModelPage.objects
            .select_related('stroyprombeton_product')
            .active()
            .filter(stroyprombeton_product__isnull=False)
        )


class CategoryPagesSitemap(AbstractSitemap):

    def items(self):
        return (
            ModelPage.objects
            .select_related('stroyprombeton_category')
            .active()
            .filter(stroyprombeton_category__isnull=False)
        )
