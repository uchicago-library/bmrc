"""Streamfields live in here"""

from django import forms
from django.core.validators import validate_slug
from wagtail import blocks
from wagtail.blocks import (
    CharBlock,
    ChoiceBlock,
    FieldBlock,
    RawHTMLBlock,
    StaticBlock,
    StreamBlock,
)
from wagtail.images.blocks import ImageChooserBlock


class RichtextBlock(blocks.RichTextBlock):
    """Richtext WYSIWYG."""

    class Meta:  # noqa
        template = "streams/richtext_block.html"
        icon = "doc-full"
        label = "Rich Text"


class PageCallout(blocks.StructBlock):
    """Homepage: Half-width callout page with text and button."""

    callout_title = blocks.CharBlock(
        required=False, help_text="Title for callout section"
    )
    callout_text = RichtextBlock(
        required=False,
        features=["bold", "italic", "ol", "ul", "link", "document-link"],
        label='Callout Text',
    )
    button_link = blocks.PageChooserBlock(
        required=False, help_text='Where you want the button to go'
    )
    button_label = blocks.CharBlock(
        required=False, help_text='Text that shows up in button'
    )

    class Meta:  # noqa
        template = "streams/page_callout.html"
        icon = "placeholder"
        label = "Page Callout"


class NewRow(blocks.StructBlock):
    """Homepage: Force a row break between columns."""

    class Meta:
        template = "streams/new_row.html"
        icon = "horizontalrule"
        label = "New Row"


class WebFeedBlock(blocks.StructBlock):
    """Code block for social media feeds."""

    webfeed_title = blocks.CharBlock(
        required=False, help_text="Title for callout section"
    )
    webfeed_code = RawHTMLBlock(required=False)

    class Meta:  # noqa
        template = "streams/webfeed_block.html"
        icon = "code"
        label = "Web Feed Block"


class ImageFormatChoiceBlock(FieldBlock):
    """Alignment options to use with the ImageBlock."""

    field = forms.ChoiceField(
        choices=(
            ('pull-left', 'Wrap left'),
            ('pull-right', 'Wrap right'),
            ('fullwidth', 'Full width'),
        )
    )


class ImageBlock(blocks.StructBlock):
    """Image streamfield block."""

    image = ImageChooserBlock(
        required=False,
    )
    caption = RichtextBlock(
        required=False,
        features=["bold", "italic", "link"],
        label='Caption',
    )
    alignment = ImageFormatChoiceBlock(required=False)

    class Meta:
        icon = 'image'
        template = 'streams/image_block.html'


class ClearBlock(blocks.StaticBlock):
    """Adds a clear between floated elements."""

    class Meta:
        icon = 'cross'
        template = 'streams/clear.html'
        label = 'Stop Float'
        admin_text = 'Stops text floating around images where placed. Use with floating images and Rich Text blocks.'


class FellowsBlock(blocks.StructBlock):
    """Image streamfield block."""

    image = ImageChooserBlock(required=False, label='Profile Photo')
    profile_text = RichtextBlock(
        required=False,
        features=["h2", "h3", "bold", "italic", "link"],
        label='Profile Text',
    )
    LARGE = 'LG'
    MEDIUM = 'MD'
    SMALL = 'SM'
    FELLOW_SIZE_CHOICES = [
        (LARGE, 'Large'),
        (MEDIUM, 'Medium'),
        (SMALL, 'Small'),
    ]
    size = ChoiceBlock(choices=FELLOW_SIZE_CHOICES, default=LARGE)
    anchor = CharBlock(
        required=False,
        max_length=50,
        help_text='Slug for anchor link',
        validators=[validate_slug],
    )

    class Meta:
        icon = 'user'
        template = 'streams/fellows_block.html'
        help_text = 'Content box with image to right and text to left.'


class MembCollSearchBlock(blocks.StructBlock):
    """Search box for Member Collections."""

    label = CharBlock(
        required=False, help_text="Optional: Label placed above search box"
    )
    # placeholder_text = CharBlock(required=False, help_text="Defaults to 'Search Member Collections'")
    search_help_text = CharBlock(
        required=False, help_text="Optional: Placed below search box"
    )

    class Meta:
        template = "streams/memb_coll_search_block.html"
        icon = "search"
        label = "Collections Search Box"


class ColumnsBlock(blocks.StreamBlock):
    """Flexbox to create columns of text; variable column count."""

    new_column = RichtextBlock(
        label="New Column",
        icon="arrow-right",
    )

    class Meta:
        template = "streams/columns_block.html"
        icon = "form"
        label = "Text Columns"
        help_text = "Recommend 2-3 columns max"


class InfoBoxStyleChoiceBlock(FieldBlock):
    """Style options to use with the InfoBoxBlock."""

    field = forms.ChoiceField(
        choices=(
            ('alert-warning', 'Warning'),
            ('alert-info', 'Informative'),
            ('alert-success', 'Success'),
            ('alert-loud', 'Larger'),
        )
    )


class InfoBoxBlock(blocks.StructBlock):
    """In page text box that stands out and shows off links or important info."""

    text = RichtextBlock(
        required=True,
        features=[
            "h2",
            "h3",
            "bold",
            "ol",
            "ul",
            "hr",
            "italic",
            "link",
            "document-link",
        ],
        label='Featured Text',
    )
    style_type = InfoBoxStyleChoiceBlock(required=True)

    class Meta:
        icon = 'doc-empty-inverse'
        template = 'streams/info_box_block.html'
        label = 'Info Box'
        help_text = 'Places text in box that stands out from rest of page content.'


class FootnoteBlock(blocks.StructBlock):
    """Small text for authorship or citation information."""

    text = RichtextBlock(
        required=False,
        features=["bold", "ol", "ul", "italic", "link", "document-link"],
        label='Footnote Text',
    )

    class Meta:
        icon = 'pick'
        template = 'streams/footnote_block.html'
        label = 'Footnote'
        help_text = 'For author credit or to list citations.'
