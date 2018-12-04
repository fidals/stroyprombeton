from django.conf import settings

from search import views as search_views, search as search_engine
from pages.models import Page
from ecommerce.forms import OrderBackcallForm

from stroyprombeton.models import Product, Category


class Search(search_views.SearchView):

    # ignore CPDBear
    search_entities = [
        search_engine.Search(
            name='category',
            #
            qs=Category.objects.active(),
            # ignore CPDBear
            fields=['name', 'specification'],
            min_similarity=settings.TRIGRAM_MIN_SIMILARITY,
        ),
        search_engine.Search(
            name='product',
            qs=Product.objects.active(),
            fields=['name', 'mark', 'specification', 'id'],
            min_similarity=settings.TRIGRAM_MIN_SIMILARITY,
        ),
        search_engine.Search(
            name='page',
            qs=Page.objects.active(),
            fields=['name'],
            min_similarity=settings.TRIGRAM_MIN_SIMILARITY,
        )
    ]

    def get_context_data(self, **kwargs):
        context = super(Search, self).get_context_data(**kwargs)

        return {
            **context,
            'backcall_form': OrderBackcallForm(),
        }


class Autocomplete(search_views.AutocompleteView):

    # ignore CPDBear
    search_entities = [
        search_engine.Search(
            name='product',
            qs=Product.objects.active(),
            fields=['name', 'code', 'mark', 'specification'],
            template_fields=['name', 'mark', 'specification', 'url'],
            min_similarity=settings.TRIGRAM_MIN_SIMILARITY,
        ),
    ]

    see_all_label = settings.SEARCH_SEE_ALL_LABEL


class AdminAutocomplete(search_views.AdminAutocompleteView):

    # ignore CPDBear
    search_entities = [
        search_engine.Search(
            name='category',
            qs=Category.objects.active(),
            # ignore CPDBear
            fields=['name'],
            min_similarity=settings.TRIGRAM_MIN_SIMILARITY,
        ),
        # ignore CPDBear
        search_engine.Search(
            name='product',
            qs=Product.objects.active(),
            fields=['name'],
            min_similarity=settings.TRIGRAM_MIN_SIMILARITY,
        ),
        search_engine.Search(
            name='pages',
            qs=Page.objects.filter(is_active=True),
            fields=['name'],
            min_similarity=settings.TRIGRAM_MIN_SIMILARITY,
        )
    ]
