from django.db.models import ObjectDoesNotExist, Value
from django.db.models.functions import Concat
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _

from generic_admin import views as admin_views
from stroyprombeton import models, forms


def category_name_strategy(entity, related_model_entity, related_model_value):
    error_message = _('Category with name ( %s ) does not exist.')
    try:
        new_category = type(related_model_entity).objects.get(name=related_model_value)
    except ObjectDoesNotExist:
        raise ValueError(error_message % related_model_value)
    entity.category = new_category


def sync_page_name(entity, value):
    entity.name = entity.page.name = value
    entity.save()
    entity.page.save()


class GenericTableEditor:
    model = models.Product
    relation_field_names = ['category', 'page', 'options']
    add_entity_form = forms.AddProductForm
    page_creation = True

    excluded_related_model_fields = {
        'page': [
            'children', 'content', 'date_published', 'id', 'images', 'level', 'lft',
            'name', 'parent', 'related_model_name', 'rght', 'stroyprombeton_category',
            'stroyprombeton_product', 'slug', 'template', 'tree_id', 'type',
        ],
    }

    included_related_model_fields = {
        'category': [
            'name',
        ],
        'options': [
            'mark',
        ],
    }

    excluded_model_fields = [
        'category', 'page', 'options', 'property', 'tags',
        'category_id', 'page_id', 'options_id', 'property_id', 'tags_id',
        'id',
    ]

    field_controller = admin_views.TableEditorFieldsControlMixin(
        models.Product,
        relation_field_names=relation_field_names,
        excluded_model_fields=excluded_model_fields,
        included_related_model_fields=included_related_model_fields,
        excluded_related_model_fields=excluded_related_model_fields,
    )


class TableEditorAPI(GenericTableEditor, admin_views.TableEditorAPI):
    pattern_to_update_model = {
        'name': sync_page_name,
    }
    pattern_to_update_related_model = {
        'category': {
            'name': category_name_strategy,
        }
    }


class TableEditor(GenericTableEditor, admin_views.TableEditor):
    pass


class Tree(admin_views.Tree):
    model = models.Category


class RedirectToProduct(admin_views.RedirectToProductPage):
    model = models.Product
    admin_page_product_urlconf = 'admin:stroyprombeton_productpage_change'
    site_page_product_urlconf = 'product'


def csv_options(request):
    # hard code url because it's template
    options = (
        models.Option.objects
        .bind_fields()
        .active()
        .annotate(label=Concat('product__name', Value(' '), 'mark'))
    )
    csv = '\n'.join([f'{o.url};{o.label}' for o in options])
    return HttpResponse(
        content_type='text/csv',
        content=csv.encode()
    )
