from catalog import context
from stroyprombeton import models as stb_models

# @todo #744:30m Move all tags related context classes in this file.


class All(context.Tags):

    def __init__(self, qs: stb_models.TagQuerySet = None):
        self._qs = qs or stb_models.Tag.objects.all()

    def qs(self) -> stb_models.OptionQuerySet:
        return self._qs
