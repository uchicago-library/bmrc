from django.db import models

from modelcluster.fields import ParentalKey

from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    PageChooserPanel,
    StreamFieldPanel,
)
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Page, Orderable
from wagtail.images.edit_handlers import ImageChooserPanel

from streams import blocks
from news.models import NewsStoryPage


class HomePageCarouselImages(Orderable):
    """Up to 3 images for the home page carousel."""

    id = models.AutoField(primary_key=True)
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
    button_link = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text='Where you want the button to go',
        related_name="+",
    )
    button_label = models.CharField(max_length=100, null=True, blank=True, help_text='Text that shows up in button')

    panels = [
        ImageChooserPanel("carousel_image"),
        FieldPanel("carousel_title"),
        FieldPanel("carousel_text"),
        PageChooserPanel("button_link"),
        FieldPanel("button_label"),
    ]
    heading="Carousel Images",


class HomePage(Page):
    """Home page model"""

    template = "home/home_page.html"
    max_count = 1
    parent_page_type = [
        'wagtailcore.Page'
    ]

    body = StreamField(
        [
            ("richtext", blocks.RichtextBlock()),
            ("page_callout", blocks.PageCallout()),
            ("webfeed", blocks.WebFeedBlock()),
            ("new_row", blocks.NewRow()),
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

    # News Feed
    def get_context(self, request):
        context = super(HomePage, self).get_context(request)
        context["news_feed"] = self.news_feed()
        return context

    def news_feed(self):
        # Order by most recent date first
        news_feed = NewsStoryPage.objects.live().public().order_by('-story_date')[:3]

        return news_feed

    class Meta:

        verbose_name = "Home Page"
        verbose_name_plural = "Home Pages"
