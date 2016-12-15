from itertools import groupby

from django.conf import settings

import pages.views
from ecommerce.forms import OrderBackcallForm
from pages.models import FlatPage


class IndexPage(pages.views.CustomPageView):
    template_name = 'pages/index/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexPage, self).get_context_data(**kwargs)

        def prepare_pages(page_parent_name, pages_):
            if page_parent_name == 'news':
                return pages_[:2]
            if page_parent_name == 'client-feedbacks':
                return pages_[:3]
            return sorted(pages_, key=lambda x: x.position)

        # Get entities by one hit on the database.
        pages_query = (
            FlatPage.objects
                .select_related('parent')
                .filter(parent__slug__in=['news', 'client-feedbacks', 'regions'], is_active=True)
                .order_by('-date_published')
                .iterator()
        )

        pages = {
            page_parent_name.replace('-', '_'): prepare_pages(page_parent_name, list(pages_))
            for page_parent_name, pages_ in
            groupby(pages_query, key= lambda x: x.parent.slug)
        }

        return {
            **context,
            **pages,
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
            'regions': list(  # Evaluate queryset to avoid performance problems.
                FlatPage.objects
                    .filter(parent__slug='regions', is_active=True)
                    .order_by('position')
                    .select_related('parent')
            )
        }
