from django.utils.translation import ugettext_lazy as _

from generic_admin import sites

from stroyprombeton.views import TableEditor


class AdminSite(sites.SiteWithTableEditor):

    site_header = _('Stroyprombeton administration')
    table_editor_view = TableEditor
