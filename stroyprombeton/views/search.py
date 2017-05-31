from django.http import JsonResponse

from catalog.views import search
from catalog.models import trigram_search
from ecommerce.forms import OrderBackcallForm

from stroyprombeton.views.helpers import MODEL_MAP


class AbstractSearch:

    model_map = MODEL_MAP

    lookups = [
        'name',
        'specification',
    ]

    minimum_similarity = 0.3

    # Warning: Dirty fix. Search CBV need refactoring
    # Tail task: https://goo.gl/FFlpFF
    def search(self, term, limit, ordering=None):
        stripped_term = term.strip()

        product_lookups = [
            'name',
            'mark',
            'specification',
        ]

        categories = trigram_search(self.category, stripped_term, self.lookups)
        products = trigram_search(self.product, stripped_term, product_lookups)

        categories = (
            categories
            .filter(similarity__gt=self.minimum_similarity)[:limit]
        )

        left_limit = limit - len(categories)
        products = (
            products
            .filter(similarity__gt=self.minimum_similarity)[:left_limit]
        )

        return categories, products


class Autocomplete(AbstractSearch, search.Autocomplete):

    see_all_label = 'Показать все результаты'

    # Extend default ordering fields
    extra_ordering_fields = ('name', 'code')

    # Extend default search fields
    extra_entity_fields = {
        'product': {
            'code',
            'mark',
            'specification',
        },
    }


class AdminAutocomplete(search.AdminAutocomplete):

    model_map = MODEL_MAP

    lookups = [
        'name',
    ]

    def get(self, request):
        term, page_type = request.GET.get('term'), request.GET.get('pageType')
        if page_type not in self.model_map:
            return

        current_model = self.model_map[page_type]

        autocomplete_items = trigram_search(
            current_model,
            term,
            self.lookups
        )[:self.autocomplete_limit]

        names = [item.name for item in autocomplete_items]

        return JsonResponse(names, safe=False)


class Search(AbstractSearch, search.Search):

    def get_context_data(self, **kwargs):
        context = super(Search, self).get_context_data(**kwargs)

        return {
            **context,
            'backcall_form': OrderBackcallForm(),
        }
