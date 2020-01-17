"""News Index and Story Pages"""
# from datetime import datetime

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from django.utils import timezone

from modelcluster.fields import ParentalKey

from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    StreamFieldPanel,
)
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Page, Orderable
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index

from streams import blocks


class NewsSideBar(Orderable):
    """Sidebar for Newsletters."""

    page = ParentalKey("news.NewsIndexPage", related_name="news_sidebar")
    sidebar_title = models.CharField(max_length=100, blank=True, null=True)
    sidebar_text = RichTextField(
        blank=True,
        null=True,
        features=["bold", "italic", "ol", "ul", "link", "document-link", "image"],
    )

    panels = [
        FieldPanel("sidebar_title"),
        FieldPanel("sidebar_text"),
    ]
    heading="Sidebar Section",


class NewsIndexPage(Page):
    """Lists all news story pages."""

    max_count = 1
    subpage_types = ['news.NewsStoryPage']

    def get_context(self, request, *args, **kwargs):
        """Custom items to context."""

        context = super().get_context(request, *args, **kwargs)
        # Get all posts
        all_posts = NewsStoryPage.objects.live().public().order_by('-story_date')

        # Paginate all posts by 9 per page
        paginator = Paginator(all_posts, 9)
        # Try to get the ?page=x value
        page = request.GET.get("page")
        try:
            # If the page exists and the ?page=x is an int
            posts = paginator.page(page)
        except PageNotAnInteger:
            # If the ?page=x is not an int; show the first page
            posts = paginator.page(1)
        except EmptyPage:
            # If the ?page=x is out of range (too high most likely)
            # Then return the last page
            posts = paginator.page(paginator.num_pages)

        context["posts"] = posts
        return context

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [InlinePanel("news_sidebar", max_num=3, label="Sidebar Section")],
            heading="Sidebar",
        ),
    ]


class NewsStoryPage(Page):
    """News story page model"""

    subpage_types = []
    parent_page_types = ['news.NewsIndexPage']

    search_fields = Page.search_fields + [
        index.SearchField('excerpt')
    ]

    lead_image = models.ForeignKey(
        "wagtailimages.Image",
        blank=True,
        null=True,
        related_name="+",
        on_delete=models.SET_NULL,
    )
    excerpt = models.TextField(max_length=300, blank=True, null=True)
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
    story_date = models.DateField(default=timezone.now, help_text='Defaults to date page was created. If you plan to publish in the future post, change to publish date here.')

    content_panels = Page.content_panels + [
        ImageChooserPanel("lead_image"),
        FieldPanel("excerpt"),
        StreamFieldPanel("body"),
        FieldPanel('story_date'),
    ]

    class Meta:

        verbose_name = "News Story"
        verbose_name_plural = "News Stories"