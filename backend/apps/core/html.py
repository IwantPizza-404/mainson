"""Очистка HTML из визуального редактора админки перед показом на сайте."""

import nh3

ALLOWED_TAGS = {
    "h2",
    "h3",
    "h4",
    "p",
    "br",
    "strong",
    "b",
    "em",
    "i",
    "u",
    "s",
    "ul",
    "ol",
    "li",
    "blockquote",
    "a",
    "hr",
    "div",
}
ALLOWED_ATTRIBUTES = {"a": {"href", "title"}}


def clean_html(value: str) -> str:
    """Оставляет только безопасную разметку: без скриптов, стилей, обработчиков событий."""
    if not value:
        return ""
    return nh3.clean(
        value,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        url_schemes={"http", "https", "mailto", "tel"},
        link_rel="noopener noreferrer",
    )
