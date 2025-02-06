"""Standard / Basic page type"""

from django.db import models

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


class SideBar(Orderable):
    """Optional Sidebar."""

    id = models.AutoField(primary_key=True)
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

    show_nested_children = models.BooleanField(
        default=False, help_text="Check this to display nested child pages."
    )

    nested_children_depth = models.PositiveIntegerField(
        default=1,
        help_text="Number of levels deep to show child pages (1 means immediate children only).",
    )

    content_panels = Page.content_panels + [
        FieldPanel("body"),
        MultiFieldPanel(
            [InlinePanel("sidebar", max_num=3, label="Sidebar Section")],
            heading="Sidebar",
        ),
        MultiFieldPanel(
            [
                FieldPanel('show_nested_children'),
                FieldPanel('nested_children_depth'),
            ],
            heading='Dynamic Page Listing',
        ),
    ]

    class Meta:

        verbose_name = "Standard Page"
        verbose_name_plural = "Standard Pages"
