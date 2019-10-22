"""Streamfields live in here"""

from wagtail.core import blocks
from wagtail.core.blocks import (RawHTMLBlock)
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
    callout_text = RichtextBlock(required=False, features=["bold", "italic", "ol", "ul", "link", "document-link"])
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


class NewRow(blocks.StructBlock):
    """Force a row break between columns."""

    class Meta:
        template = "streams/new_row.html"
        icon = "horizontalrule"
        label = "New Row"
