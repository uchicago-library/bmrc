"""Shared validators for content accessibility."""

import re
from html.parser import HTMLParser

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


_GENERIC_ALT_WORDS = {
    "image",
    "photo",
    "picture",
    "graphic",
    "icon",
    "logo",
    "img",
    "art",
    "artwork",
    "thumbnail",
    "figure",
}

_INVALID_ALT_VALUES = {"", "-", "--", ".", "na", "n/a", "none", "null", "untitled"}

_FILE_EXTENSION_PATTERN = re.compile(
    r"\.(jpe?g|png|gif|bmp|svg|webp|tiff?|ico)$", re.IGNORECASE
)


def _normalize_alt_text(value):
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    return text


def _normalized_alt_words(value):
    cleaned = re.sub(r"[^a-z0-9\s]", "", value.lower()).strip()
    return [word for word in cleaned.split() if word]


def validate_alt_text(value):
    """Validate that alt text is present and minimally descriptive."""
    text = _normalize_alt_text(value)
    
    # Check for empty or placeholder values
    if text.lower() in _INVALID_ALT_VALUES:
        raise ValidationError(
            _("Alt text is required and cannot be empty or a placeholder."),
            code="alt_text_required",
        )

    # Check minimum length
    if len(text) < 3:
        raise ValidationError(
            _("Alt text must be at least 3 characters long."),
            code="alt_text_too_short",
        )

    # Check if it's only numbers
    if text.replace(" ", "").isdigit():
        raise ValidationError(
            _("Alt text cannot be only numbers. Describe what the image shows."),
            code="alt_text_only_numbers",
        )

    # Check for file extensions
    if _FILE_EXTENSION_PATTERN.search(text):
        raise ValidationError(
            _("Alt text should not contain file names or extensions. Describe what the image shows."),
            code="alt_text_filename",
        )

    # Check if it looks like a URL or file path
    if any(pattern in text.lower() for pattern in ["http://", "https://", "www.", ".com", "\\", "/"]):
        raise ValidationError(
            _("Alt text should not contain URLs or file paths. Describe what the image shows."),
            code="alt_text_url",
        )

    # Check if all words are generic
    words = _normalized_alt_words(text)
    if words and set(words).issubset(_GENERIC_ALT_WORDS):
        raise ValidationError(
            _("Alt text must be more descriptive than a generic label like 'image' or 'photo'."),
            code="alt_text_too_generic",
        )


class _RichTextImageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.images = []  # Store (alt, is_decorative, is_richtext_image) tuples

    def _is_truthy(self, value):
        return str(value).lower() in {"1", "true", "yes", "on"}

    def _is_decorative(self, attr_map):
        for key, value in attr_map.items():
            if "decorative" in key and self._is_truthy(value):
                return True
        if "decorative" in attr_map.get("class", "").lower():
            return True
        return False

    def handle_starttag(self, tag, attrs):
        normalized_tag = tag.lower()
        attr_map = {key.lower(): value for key, value in attrs}

        if normalized_tag == "img":
            is_decorative = self._is_decorative(attr_map)
            class_value = attr_map.get("class", "")
            is_richtext_image = "richtext-image" in class_value.lower()
            self.images.append((attr_map.get("alt"), is_decorative, is_richtext_image))
            return

        embed_type = (
            attr_map.get("embedtype")
            or attr_map.get("data-embedtype")
            or attr_map.get("data-wagtail-embedtype")
        )
        if normalized_tag == "embed" and embed_type == "image":
            is_decorative = self._is_decorative(attr_map)
            class_value = attr_map.get("class", "")
            is_richtext_image = "richtext-image" in class_value.lower()
            self.images.append((attr_map.get("alt"), is_decorative, is_richtext_image))


def validate_richtext_images_alt_text(value):
    """Validate that all richtext images include minimally descriptive alt text.
    
    Images with alt text must have descriptive content.
    """
    html = value.source if hasattr(value, "source") else str(value or "")
    parser = _RichTextImageParser()
    parser.feed(html)

    for index, (alt, _is_decorative, _is_richtext_image) in enumerate(
        parser.images, start=1
    ):
        if alt is None or not alt.strip():
            continue

        try:
            validate_alt_text(alt)
        except ValidationError as exc:
            raise ValidationError(
                _("Image %(index)s alt text is not descriptive enough."),
                code="alt_text_invalid",
                params={"index": index},
            ) from exc
