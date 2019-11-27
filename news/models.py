"""News Index and Story Pages"""
# from datetime import datetime

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from django.utils import timezone

from wagtail.admin.edit_handlers import (
    FieldPanel,
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