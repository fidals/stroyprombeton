from itertools import groupby

from django.conf import settings
from django.shortcuts import render
from mptt.utils import get_cached_trees

import pages.views
from ecommerce.forms import OrderBackcallForm
from pages.models import FlatPage, CustomPage


def fetch_reviews(request):
    """Fetch reviews with images for gallery."""
    first_triple = [1, 2, 3]
    reviews = FlatPage.objects.all().exclude(position__in=first_triple).order_by('position')

    return render(
        request,
        'pages/index/review_items.html',
        {'reviews': reviews}
    )


def get_cached_regions():
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

        def prepare_pages(parent_slug, pages_):
            if parent_slug == 'news':
                return sorted(pages_, key=lambda x: x.date_published, reverse=True)[:2]
            if parent_slug == 'client-feedbacks':
                return sorted(pages_, key=lambda x: x.position)[:3]

        pages_query = (
            FlatPage.objects
                .select_related('parent')
                .filter(parent__slug__in=['news', 'client-feedbacks'], is_active=True)
                .iterator()
        )

        pages = {
            parent_slug.replace('-', '_'): prepare_pages(parent_slug, list(pages_))
            for parent_slug, pages_ in
            groupby(pages_query, key=lambda x: x.parent.slug)
        }

        return {
            **context,
            **pages,
            'backcall_form': OrderBackcallForm(),
            'partners': settings.PARTNERS,
            'regions': get_cached_regions(),
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
