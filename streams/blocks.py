"""Streamfields live in here"""

from wagtail.core import blocks
from wagtail.images.blocks import ImageChooserBlock

class RichtextBlock(blocks.RichTextBlock):
	"""Richtext WYSIWYG"""

	class Meta:  # noqa
		template = "streams/richtext_block.html"
		icon = "doc-full"
		label = "Rich Text"
