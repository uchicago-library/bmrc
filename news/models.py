"""News Index and Story Pages"""
# from datetime import datetime

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from django.utils import timezone

from modelcluster.fields import ParentalKey

from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
)
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page, Orderable
from wagtail.search import index

from streams import blocks


class NewsSideBar(Orderable):
    """Sidebar for Newsletters."""

    id = models.AutoField(primary_key=True)
    page = ParentalKey("news.NewsIndexPage", related_name="news_sidebar")
    sidebar_title = models.CharField(max_length=100, blank=True, null=True)
    sidebar_text = RichTextField(
        blank=True,
        null=True,
        features=[
            "bold", "italic", "ol", "ul", "link", "document-link", "image"
        ],
    )

    panels = [
        FieldPanel("sidebar_title"),
        FieldPanel("sidebar_text"),
    ]
    heading = "Sidebar Section",


class NewsIndexPage(Page):
    """Lists all news story pages."""

    max_count = 1
    subpage_types = ['news.NewsStoryPage', 'news.NewsletterSignupPage']

    def get_context(self, request, *args, **kwargs):
        """Custom items to context."""

        context = super().get_context(request, *args, **kwargs)
        # Get all posts
        all_posts = NewsStoryPage.objects.live().public().order_by(
            '-story_date')

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

    search_fields = Page.search_fields + [index.SearchField('excerpt')]

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
            ("richtext", blocks.RichtextBlock(group="Format and Text")),
            ("two_column_block", blocks.ColumnsBlock(group="Format and Text")),
            ("info_box_block", blocks.InfoBoxBlock(group="Format and Text")),
            ("footnote_block", blocks.FootnoteBlock(group="Format and Text")),
            ("image_block", blocks.ImageBlock(group="Layout and Images")),
            ("fellows_block", blocks.FellowsBlock(group="Layout and Images")),
            ("clear_block", blocks.ClearBlock(group="Layout and Images")),
        ],
        null=True,
        blank=True,
    )
    story_date = models.DateField(
        default=timezone.now,
        help_text=
        'Defaults to date page was created. If you plan to publish in the future post, change to publish date here.'
    )

    content_panels = Page.content_panels + [
        FieldPanel("lead_image"),
        FieldPanel("excerpt"),
        FieldPanel("body"),
        FieldPanel('story_date'),
    ]

    class Meta:

        verbose_name = "News Story"
        verbose_name_plural = "News Stories"


class NewsletterSignupPage(Page):
    """Page for embedded Newsletter form code"""

    max_count = 1
    subpage_types = []
    parent_page_types = ['news.NewsIndexPage']

    search_fields = Page.search_fields + [
        index.SearchField('search_description')
    ]

    body = StreamField(
        [
            ("richtext", blocks.RichtextBlock()),
            ("webfeed", blocks.WebFeedBlock()),
            ("image_block", blocks.ImageBlock()),
        ],
        null=True,
        blank=True,
    )

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]

    class Meta:

        verbose_name = "Newsletter Form"
        verbose_name_plural = "Newsletter Forms"
