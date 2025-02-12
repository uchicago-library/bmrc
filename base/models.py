from streams import blocks
from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtail.models import Page
from wagtail.search import index


class AbstractBasePage(Page):
    class Meta:
        abstract = True

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

    content_panels = Page.content_panels + [FieldPanel('body')]

    search_fields = Page.search_fields + [
        index.SearchField('body'),
    ]
