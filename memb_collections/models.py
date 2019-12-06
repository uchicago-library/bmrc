"""Member Collection Search page type"""

from django.db import models

from modelcluster.fields import ParentalKey

from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    StreamFieldPanel,
)
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Page, Orderable

from streams import blocks


class SideBar(Orderable):
    """Optional Sidebar."""

    page = ParentalKey("memb_collections.MembCollectionIndexPage", related_name="sidebar")
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


class MembCollectionIndexPage(Page):
    """Landing page for member collection search box"""

    template = "memb_collections/memb_collections_index_page.html"
    max_count = 1
    subpage_types = []
    parent_page_types = ['home.HomePage']

    body = StreamField(
        [
            ("richtext", blocks.RichtextBlock()),
            ("image_block", blocks.ImageBlock()),
            ("new_row", blocks.NewRow()),
            ("memb_coll_search_block", blocks.MembCollSearchBlock()),
        ],
        null=True,
        blank=True,
    )

    content_panels = Page.content_panels + [
        StreamFieldPanel("body"),
        MultiFieldPanel(
            [InlinePanel("sidebar", max_num=3, label="Sidebar Section")],
            heading="Sidebar",
        ),
    ]

    class Meta:

        verbose_name = "Member Collection Index Page"
        verbose_name_plural = "Member Collection Index Pages"