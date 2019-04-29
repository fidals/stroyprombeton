from django.contrib.redirects.models import Redirect

from generic_admin import models as rf_admin_models
from pages import models as pages_models

from stroyprombeton import models as stb_models

from . import sites, models as admin_models

admin_site = sites.AdminSite(name='stb_admin')

# Pages
admin_site.register(pages_models.PageTemplate, rf_admin_models.CustomPageTemplateAdmin)
admin_site.register(pages_models.CustomPage, admin_models.CustomPageAdmin)
admin_site.register(pages_models.FlatPage, admin_models.FlatPageAdmin)

# STB
admin_site.register(stb_models.ProductPage, admin_models.ProductPageAdmin)
admin_site.register(stb_models.CategoryPage, admin_models.CategoryPageAdmin)
admin_site.register(stb_models.NewsForAdmin, admin_models.FlatPageAdmin)
admin_site.register(stb_models.RegionsForAdmin, admin_models.FlatPageAdmin)
admin_site.register(stb_models.ClientFeedbacksForAdmin, admin_models.FlatPageAdmin)
admin_site.register(stb_models.Order, admin_models.OrderAdmin)
admin_site.register(stb_models.Option, admin_models.OptionAdmin)
admin_site.register(stb_models.SeriesPage, admin_models.SeriesPageAdmin)

# Redirects
admin_site.register(Redirect)
