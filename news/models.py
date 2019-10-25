"""News Index and Story Pages"""

from django.db import models

from wagtail.admin.edit_handlers import (
	FieldPanel,
	# InlinePanel,
	# MultiFieldPanel,
	StreamFieldPanel,
)
from wagtail.core.fields import StreamField
from wagtail.core.models import Page
from wagtail.images.edit_handlers import ImageChooserPanel

from streams import blocks


class NewsIndexPage(Page):
	"""Lists all news story pages."""

	# template = "blog/blog_listing_page.html"
	# ajax_template = "blog/blog_listing_page_ajax.html"
	max_count = 1
	subpage_types = ['news.NewsStoryPage']

	def get_context(self, request, *args, **kwargs):
		"""Custom items to context."""
		context = super().get_context(request, *args, **kwargs)
		# Get all posts
		context["posts"] = NewsStoryPage.objects.live().public().order_by('-first_published_at')
		return context


class NewsStoryPage(Page):
	"""News story page model"""

	# template = "standard/standard_page.html"

	subpage_types = []
	parent_page_types = ['news.NewsIndexPage']

	lead_image = models.ForeignKey(
		"wagtailimages.Image",
		blank=True,
		null=True,
		related_name="+",
		on_delete=models.SET_NULL,
	)
	excerpt = models.CharField(max_length=300, blank=True, null=True)
	body = StreamField(
		[
			("richtext", blocks.RichtextBlock()),
			("page_callout", blocks.PageCallout()),
			("image_block", blocks.ImageBlock()),
			("new_row", blocks.NewRow()),
		],
		null=True,
		blank=True,
	)

	content_panels = Page.content_panels + [
		ImageChooserPanel("lead_image"),
		FieldPanel("excerpt"),
		StreamFieldPanel("body"),
	]

	class Meta:

		verbose_name = "News Story"
		verbose_name_plural = "News Stories"