"""Standard / Basic page type"""

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
from wagtail.search import index

from streams import blocks


class SideBar(Orderable):
    """Optional Sidebar."""

    page = ParentalKey("standard.StandardPage", related_name="sidebar")
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


class StandardPage(Page):
    """Standard page model"""

    template = "standard/standard_page.html"

    search_fields = Page.search_fields + [
        index.SearchField('search_description')
    ]

    body = StreamField(
        [
            ("richtext", blocks.RichtextBlock(group="Format and Text")),
            ("two_column_block", blocks.ColumnsBlock(group="Format and Text")),
            ("info_box_block", blocks.InfoBoxBlock(group="Format and Text")),
            ("footnote_block", blocks.FootnoteBlock(group="Format and Text")),
            ("image_block", blocks.ImageBlock(group="Layout and Images")),
            ("fellows_block", blocks.FellowsBlock(group="Layout and Images")),
            ("clear_block", blocks.ClearBlock(group="Layout and Images")),
            ("webfeed", blocks.WebFeedBlock(group="Layout and Images")),
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

        verbose_name = "Standard Page"
        verbose_name_plural = "Standard Pages"