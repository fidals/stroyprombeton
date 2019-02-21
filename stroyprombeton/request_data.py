import typing

from django import http
from django_user_agents.utils import get_user_agent


# @todo #431:15m  Move Request class to refarm side. se2
class Request:
    """Comprehensive request entity: django's request + url arguments."""

    def __init__(
        self, request: http.HttpRequest, url_kwargs: typing.Dict[str, str]
    ):
        """:param request: came here throw django urls and django views."""
        self.request = request
        self.url_kwargs = url_kwargs


class Category(Request):
    PRODUCTS_ON_PAGE_PC = 48
    PRODUCTS_ON_PAGE_MOB = 12

    @property
    def id(self):
        return self.url_kwargs.get('category_id')

    @property
    def length(self):
        """Max size of products list depends on the device type."""
        is_mobile = get_user_agent(self.request).is_mobile
        return (
            self.PRODUCTS_ON_PAGE_MOB
            if is_mobile else self.PRODUCTS_ON_PAGE_PC
        )

    @property
    def tags(self) -> str:
        return self.url_kwargs.get('tags', '')

    # FetchProducts inherits unused pagination stuff.
    # se#731 will fix this ussue.
    @property
    def pagination_page_number(self):
        return int(self.request.GET.get('page', 1))

    @property
    def pagination_per_page(self):
        return int(self.request.GET.get('step', self.length))


class FetchProducts(Category):

    @property
    def id(self):
        # @todo #443:15m Check FetchProducts post params.
        #  Raise Http400 if categoryId not exists.
        #  See `Http400` error on SE for example.
        return self.request.POST.get('categoryId')

    @property
    def filtered(self) -> bool:
        value = self.request.POST.get('filtered', '')
        return value == 'true'

    @property
    def term(self) -> str:
        return self.request.POST.get('term', '').strip()

    @property
    def offset(self):
        return int(self.request.POST.get('offset', 0))

    @property
    def length(self):
        return int(self.request.POST.get('limit', self.PRODUCTS_ON_PAGE_PC))
