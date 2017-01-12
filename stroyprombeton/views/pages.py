from itertools import groupby

from django.conf import settings
from mptt.utils import get_cached_trees

import pages.views
from ecommerce.forms import OrderBackcallForm
from pages.models import FlatPage, CustomPage


def get_cached_regions():
    CustomPage.objects.get(slug='regions').get_children()
    regions_query = (
        CustomPage.objects
            .prefetch_related('children')
            .filter(slug='regions')
            .first()
    )

    cached_regions = get_cached_trees(
        [regions_query, *regions_query.children.all()]
    )

    return sorted(cached_regions[0].get_children(), key=lambda x: x.position)


class IndexPage(pages.views.CustomPageView):
    template_name = 'pages/index/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexPage, self).get_context_data(**kwargs)

        def prepare_pages(page_parent_name, pages_):
            if page_parent_name == 'news':
                return pages_[:2]
            if page_parent_name == 'client-feedbacks':
                return pages_[:3]

        pages_query = (
            FlatPage.objects
                .select_related('parent')
                .filter(parent__slug__in=['news', 'client-feedbacks'], is_active=True)
                .order_by('-date_published')
                .iterator()
        )

        pages = {
            page_parent_name.replace('-', '_'): prepare_pages(page_parent_name, list(pages_))
            for page_parent_name, pages_ in
            groupby(pages_query, key=lambda x: x.parent.slug)
        }

        return {
            **context,
            **pages,
            'regions': get_cached_regions(),
            'partners': settings.PARTNERS,
            'backcall_form': OrderBackcallForm(),
        }


class NewsPageView(pages.views.CustomPageView):
    template_name = 'pages/page.html'


class RegionsPageView(pages.views.CustomPageView):
    template_name = 'pages/regions/region_page.html'

    def get_context_data(self, **kwargs):
        context = super(RegionsPageView, self).get_context_data(**kwargs)

        return {
            **context,
            'regions': get_cached_regions()
        }
