from typing import TypeVar

from config.i18n import _
from utils.exceptions import Custom404Exception


T = TypeVar("T")


def get_object_or_404(obj: T | None, *, msg: str | None = None) -> T:
    msg = _(msg) if msg else _("Not found.")
    if obj is None:
        raise Custom404Exception(msg)
    return obj
