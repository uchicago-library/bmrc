"""Streamfields live in here"""

from django import forms
from wagtail.core import blocks
from wagtail.core.blocks import (CharBlock, FieldBlock, RawHTMLBlock)
from wagtail.images.blocks import ImageChooserBlock


class RichtextBlock(blocks.RichTextBlock):
    """Richtext WYSIWYG."""

    class Meta:  # noqa
        template = "streams/richtext_block.html"
        icon = "doc-full"
        label = "Rich Text"


class PageCallout(blocks.StructBlock):
    """Half-width callout page with text and button."""

    callout_title = blocks.CharBlock(required=False, help_text="Title for callout section")
    callout_text = RichtextBlock(
        required=False,
        features=["bold", "italic", "ol", "ul", "link", "document-link"],
        label='Callout Text',
    )
    button_link = blocks.PageChooserBlock(required=False, help_text='Where you want the button to go')
    button_label = blocks.CharBlock(required=False, help_text='Text that shows up in button')

    class Meta:  # noqa
        template = "streams/page_callout.html"
        icon = "placeholder"
        label = "Page Callout"


class WebFeedBlock(blocks.StructBlock):
    """Code block for social media feeds."""

    webfeed_title = blocks.CharBlock(required=False, help_text="Title for callout section")
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

    image = ImageChooserBlock(required=False,)
    caption = RichtextBlock(
        required=False,
        features=["bold", "italic", "link"],
        label='Caption',
    )
    alignment = ImageFormatChoiceBlock(required=False)

    class Meta:
        icon = 'image'
        template = 'streams/image_block.html'


class NewRow(blocks.StructBlock):
    """Force a row break between columns."""

    class Meta:
        template = "streams/new_row.html"
        icon = "horizontalrule"
        label = "New Row"


class FellowsBlock(blocks.StructBlock):
    """Image streamfield block."""

    image = ImageChooserBlock(required=False, label='Profile Photo')
    profile_text = RichtextBlock(
        required=False,
        features=["bold", "italic", "link"],
        label='Profile Text',
    )

    class Meta:
        icon = 'user'
        template = 'streams/fellows_block.html'


class MembCollSearchBlock(blocks.StructBlock):
    """Search box for Member Collections."""

    label = CharBlock(required=False, help_text="Optional: Label placed above search box")
    # placeholder_text = CharBlock(required=False, help_text="Defaults to 'Search Member Collections'")
    search_help_text = CharBlock(required=False, help_text="Optional: Placed below search box")

    class Meta:
        template = "streams/memb_coll_search_block.html"
        icon = "search"
        label = "Collections Search Box"



