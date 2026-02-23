from django import template


register = template.Library()


_MISSING = object()


def _get_value(source, field_name):
    if isinstance(source, dict):
        return source.get(field_name, _MISSING)
    return getattr(source, field_name, _MISSING)


@register.filter
def alt_text_attr(value):
    """Return alt text value for image-like objects with decorative support."""
    if value is None:
        return ""

    is_decorative = _get_value(value, "is_decorative")
    if is_decorative is _MISSING:
        is_decorative = _get_value(value, "lead_image_is_decorative")
    if is_decorative:
        return ""

    alt_text = _get_value(value, "alt_text")
    if alt_text is _MISSING:
        alt_text = _get_value(value, "lead_image_alt_text")

    if alt_text in {_MISSING, None}:
        return ""

    return alt_text
