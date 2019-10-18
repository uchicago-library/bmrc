from django.db import models

from modelcluster.fields import ParentalKey

from wagtail.admin.edit_handlers import (
	FieldPanel,
	InlinePanel,
	MultiFieldPanel,
	PageChooserPanel,
	StreamFieldPanel,
)
from wagtail.core.models import Page, Orderable
from wagtail.core.fields import RichTextField, StreamField
from wagtail.images.edit_handlers import ImageChooserPanel

from streams import blocks


class HomePageCarouselImages(Orderable):
	"""Up to 3 images for the home page carousel."""

	page = ParentalKey("home.HomePage", related_name="carousel_images")
	carousel_image = models.ForeignKey(
		"wagtailimages.Image",
		null=True,
		blank=True,
		on_delete=models.SET_NULL,
		related_name="+",
	)
	carousel_title = models.CharField(max_length=100, blank=True, null=True)
	carousel_text = RichTextField(blank=True, null=True)
	carousel_button = models.ForeignKey(
		"wagtailcore.Page",
		null=True,
		blank=True,
		on_delete=models.SET_NULL,
		related_name="+",
	)

	panels = [
		ImageChooserPanel("carousel_image"),
		FieldPanel("carousel_title"),
		FieldPanel("carousel_text"),
		PageChooserPanel("carousel_button"),
	]
	heading="Carousel Images",

	# api_fields = [
	# 	APIField("carousel_image"),
	# ]


class HomePage(Page):
	"""Home page model"""

	template = "home/home_page.html"
	parent_page_type = [
		'wagtailcore.Page'
	]

	body = StreamField(
		[
			("richtext", blocks.RichtextBlock()),
		],
		null=True,
		blank=True,
	)

	content_panels = Page.content_panels + [
		MultiFieldPanel(
			[InlinePanel("carousel_images", max_num=3, label="Image")],
			heading="Carousel Images",
		),
		StreamFieldPanel("body"),
	]

	class Meta:

		verbose_name = "Home Page"
		verbose_name_plural = "Home Pages"
