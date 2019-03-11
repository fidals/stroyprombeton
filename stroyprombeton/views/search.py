from django.conf import settings

from ecommerce.forms import OrderBackcallForm
from pages.models import CustomPage, FlatPage, Page
from search import views as search_views, search as search_engine
from stroyprombeton import models as stb_models


class Search(search_views.SearchView):

    # ignore CPDBear
    search_entities = [
        search_engine.Search(
            name='category',
            qs=stb_models.Category.objects.active(),
            # ignore CPDBear
            fields=['name', 'specification'],
            min_similarity=settings.TRIGRAM_MIN_SIMILARITY,
        ),
        search_engine.Search(
            name='product',
            qs=stb_models.Product.objects.active(),
            fields=['name', 'id'],
            min_similarity=settings.TRIGRAM_MIN_SIMILARITY,
        ),
        search_engine.Search(
            name='product',
            qs=stb_models.Option.objects.active(),
            # @todo #483:60m  Implement search by option.
            #  Return back searching by `option.specification` field.
            #  And test it of course.
            fields=['mark'],
            min_similarity=settings.TRIGRAM_MIN_SIMILARITY,
        ),
        search_engine.Search(
            name='page',
            qs=CustomPage.objects.active(),
            fields=['name'],
            min_similarity=settings.TRIGRAM_MIN_SIMILARITY,
        ),
        search_engine.Search(
            name='page',
            qs=FlatPage.objects.active(),
            fields=['name'],
            min_similarity=settings.TRIGRAM_MIN_SIMILARITY,
        ),
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
            qs=stb_models.Option.objects.active(),
            fields=['code', 'mark'],
            template_fields=['mark', 'url'],
            min_similarity=settings.TRIGRAM_MIN_SIMILARITY,
        ),
        search_engine.Search(
            name='product',
            qs=stb_models.Product.objects.active(),
            fields=['name'],
            template_fields=['name'],
            min_similarity=settings.TRIGRAM_MIN_SIMILARITY,
        ),
    ]

    see_all_label = settings.SEARCH_SEE_ALL_LABEL


class AdminAutocomplete(search_views.AdminAutocompleteView):

    # ignore CPDBear
    search_entities = [
        search_engine.Search(
            name='category',
            qs=stb_models.Category.objects.active(),
            # ignore CPDBear
            fields=['name'],
            min_similarity=settings.TRIGRAM_MIN_SIMILARITY,
        ),
        # ignore CPDBear
        search_engine.Search(
            name='product',
            qs=stb_models.Product.objects.active(),
            fields=['name'],
            min_similarity=settings.TRIGRAM_MIN_SIMILARITY,
        ),
        search_engine.Search(
            name='pages',
            qs=Page.objects.active(),
            fields=['name'],
            min_similarity=settings.TRIGRAM_MIN_SIMILARITY,
        )
    ]
