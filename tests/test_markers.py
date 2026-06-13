"""Test taxonomy markers for white-box / gray-box / black-box classification.

Attach ``__test_box__`` to a test class with the decorators below, or rely on
module defaults (see ``classification_for``).
"""

from __future__ import annotations

WHITE_BOX = "white"
GRAY_BOX = "gray"
BLACK_BOX = "black"

BOX_LABELS = {
    WHITE_BOX: "白盒 (White-box)",
    GRAY_BOX: "灰盒 (Gray-box)",
    BLACK_BOX: "黑盒 (Black-box)",
}

# Modules whose tests default to gray-box unless a class overrides.
_GRAY_MODULES = frozenset({
    "test_smart_city_extensions",
    "test_template_extension",
    "test_template_frontend_parity",
    "test_frontend_static_contracts",
})


def white_box(test_cls):
    test_cls.__test_box__ = WHITE_BOX
    return test_cls


def gray_box(test_cls):
    test_cls.__test_box__ = GRAY_BOX
    return test_cls


def black_box(test_cls):
    test_cls.__test_box__ = BLACK_BOX
    return test_cls


def classification_for(test) -> str:
    cls = test.__class__
    box = getattr(cls, "__test_box__", None)
    if box:
        return box
    module = cls.__module__.split(".")[-1]
    if module in _GRAY_MODULES:
        return GRAY_BOX
    return WHITE_BOX
