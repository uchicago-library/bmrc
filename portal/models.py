import datetime, random, urllib
from . import get_collections
from django.conf import settings
from django.db import models
from modelcluster.fields import ParentalKey
from pygments import highlight
from streams import blocks
from wagtail.admin.edit_handlers import (
    FieldPanel, 
    HelpPanel, 
    InlinePanel,
    MultiFieldPanel,
    PageChooserPanel, 
    StreamFieldPanel,
)
from wagtail.core.fields import (
    RichTextField, 
    StreamField,
)
from wagtail.core.models import (
    Orderable, 
    Page
)
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.images.models import Image
from wagtail.search import index


class Archive(models.Model):
    """BMRC Archive"""

    name = models.CharField(
        blank=False,
        help_text='Archive name.',
        max_length=200
    )
    address = models.CharField(
        blank=True,
        help_text='Street address.',
        max_length=400
    )
    link = RichTextField(
        blank=True,
        help_text='Link back to archive homepage, contact page, or other informational page.',
        max_length=2000
    )
    logo = models.ForeignKey(
        "wagtailimages.Image",
        blank=True,
        help_text='archive logo.',
        null=True,
        related_name="+",
        on_delete=models.SET_NULL
    )
    spotlight = RichTextField(
        blank=True,
        help_text='Spotlight text for the portal homepage.'
    )
    finding_aid_prefix = models.CharField(
        blank=False,
        help_text='Prefix that associates specific EAD filenames with this archive, in the form "BMRC.<ARCHIVE-NAME>"',
        max_length=200
    )
    is_member = models.BooleanField(
        default=True,
        help_text='Member archives will be included in the portal homepage rotation.'
    )
    order = models.IntegerField(
        default=1000,
        help_text='Choose the order this archive should appear in when featured on the portal homepage.'
    )

    def uri(self):
        return '{}{}'.format(
            'https://bmrc.lib.uchicago.edu/archives/',
            urllib.parse.quote_plus(self.name)
        )

    def __str__(self):
        return self.name

    @classmethod
    def featured_archive_by_date(obj, d):
        """Get the featured archive by month (helper function for testing and reporting.)"""
        unix_epoch = datetime.date(1970, 1, 1)
        month_number = (d.year - unix_epoch.year) * 12 \
                     + (d.month - unix_epoch.month)
        # adjust so that lowest order index appears in Feb 2022. 
        month_number += 21
        members = Archive.objects.filter(is_member=True).exclude(finding_aid_prefix='BMRC').order_by('order')
        try:
            return members[month_number % len(members)]
        except ZeroDivisionError:
            return None

    @classmethod
    def featured_archive(obj):
        """Rotate the featured archive once a month."""
        d = datetime.date.today()
        return Archive.featured_archive_by_date(d)


class CuratedTopicIndexPage(Page):
    """ """

    search_fields = Page.search_fields + [
        index.SearchField('body')
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
        StreamFieldPanel('body'),
        MultiFieldPanel(
            [InlinePanel('sidebar', max_num=3, label='Sidebar Section')],
            heading='Sidebar',
        ),
    ]

    parent_page_types = [
        'portal.PortalHomePage'
    ]

    subpage_types = [
        'portal.CuratedTopicPage'
    ]

    max_count = 1

    @property
    def featured_curated_topic(self):
        """Get featured topic."""
        return CuratedTopicPage.featured_curated_topic


class CuratedTopicIndexSideBar(Orderable):
    """Optional Sidebar."""

    id = models.AutoField(primary_key=True)
    page = ParentalKey('portal.CuratedTopicIndexPage', related_name='sidebar')
    sidebar_title = models.CharField(max_length=100, blank=True, null=True)
    sidebar_text = RichTextField(
        blank=True,
        null=True,
        features=[
            'bold', 'italic', 'ol', 'ul', 'link', 'document-link', 'image'
        ],
    )

    panels = [
        FieldPanel('sidebar_title'),
        FieldPanel('sidebar_text'),
    ]
    heading = 'Sidebar Section',


class CuratedTopicPage(Page):
    """ """

    image = models.ForeignKey(
        "wagtailimages.Image",
        blank=True,
        help_text='A small version of this image will display on the portal \
                   homepage, and a large version will display at the top of \
                   each curated topic page.',
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    caption = models.CharField(
        blank=True,
        help_text='Displays underneath the image on the curated topic page \
                   and as alt text.',
        max_length=400,
    )

    body = RichTextField(
        blank=True,
        null=True
    ) 

    byline = models.CharField(
        blank=True,
        help_text='Author name, appears below the body.',
        max_length=200
    )

    search_url = models.URLField(
        blank=False,
        max_length=2000
    )

    bottom_text = RichTextField(
        blank=True,
        null=True
    ) 

    content_panels = Page.content_panels + [
        ImageChooserPanel('image'),
        FieldPanel('caption'),
        FieldPanel('body'),
        FieldPanel('byline'),
        FieldPanel('search_url'),
        FieldPanel('bottom_text'),
    ]

    search_fields = Page.search_fields + [
        index.SearchField('caption'),
        index.SearchField('body'),
        index.SearchField('byline'),
        index.SearchField('bottom_text'),
    ]

    parent_page_types = [
        'portal.CuratedTopicIndexPage'
    ]

    subpage_types = []

    @classmethod
    def featured_curated_topic(cls):
        """Rotate the featured curated topic once a week."""
        week_number = abs(
            datetime.date.today() - 
            datetime.date(1970, 1, 1)
        ).days // 7
        try:
            i = week_number % len(cls.objects.live())
            return cls.objects.live()[i]
        except ZeroDivisionError:
            return None


class ExhibitIndexPage(Page):
    """ """

    search_fields = Page.search_fields + [
        index.SearchField('body')
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
        StreamFieldPanel('body'),
        MultiFieldPanel(
            [InlinePanel('sidebar', max_num=3, label='Sidebar Section')],
            heading='Sidebar',
        ),
    ]

    parent_page_types = [
        'portal.PortalHomePage'
    ]

    subpage_types = [
        'portal.ExhibitPage'
    ]

    max_count = 1

    @property
    def exhibits(self):
        return ExhibitPage.objects.live()


class ExhibitIndexSideBar(Orderable):
    """Optional Sidebar."""

    id = models.AutoField(primary_key=True)
    page = ParentalKey('portal.ExhibitIndexPage', related_name='sidebar')
    sidebar_title = models.CharField(max_length=100, blank=True, null=True)
    sidebar_text = RichTextField(
        blank=True,
        null=True,
        features=[
            'bold', 'italic', 'ol', 'ul', 'link', 'document-link', 'image'
        ],
    )

    panels = [
        FieldPanel('sidebar_title'),
        FieldPanel('sidebar_text'),
    ]
    heading = 'Sidebar Section',


class ExhibitPage(Page):
    image = models.ForeignKey(
        "wagtailimages.Image",
        blank=True,
        help_text='A small version of this image will display on the portal \
                   homepage. It does NOT appera on the ExhibitPage itself.',
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

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
        ImageChooserPanel('image'),
        StreamFieldPanel('body'),
        MultiFieldPanel(
            [InlinePanel('sidebar', max_num=3, label='Sidebar Section')],
            heading='Sidebar',
        ),
    ]

    parent_page_types = [
        'portal.ExhibitIndexPage',
        'portal.ExhibitPage'
    ]

    subpage_types = [
        'portal.ExhibitPage'
    ]


class ExhibitPageSideBar(Orderable):
    """Optional Sidebar."""

    id = models.AutoField(primary_key=True)
    page = ParentalKey("portal.ExhibitPage", related_name="sidebar")
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
    heading = "Sidebar Section"


class PortalHomePage(Page):
    """Portal home page model"""

    introduction = RichTextField(
        blank=True,
        null=True
    )
    featured_exhibit = models.ForeignKey(
        'portal.ExhibitPage',
        blank=True,
        help_text='Choose which exhibit to highlight.',
        null=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    about_the_bmrc = RichTextField(
        blank=True,
        null=True
    )

    content_panels = Page.content_panels + [
        FieldPanel('introduction'),
        HelpPanel(
            content='The featured curated topic automatically changes every \
                     week, cycling through all live CuratedTopicPages. \
                     Set the image that appears for the currently selected \
                     curated topic on that specific CuratedTopicPage.',
            heading='Curated Topics'
        ),
        PageChooserPanel('featured_exhibit', 'portal.ExhibitPage'),
        HelpPanel(
            content='The featured topic is chosen randomly, from all facets \
                     except archives,  each time the portal homepage is \
                     reloaded. To change the image that illustrates the \
                     featured topic, upload a new image in the Wagtail admin. \
                     Images should have one of the following titles: \
                     homepage_facet_image_topics.jpg, \
                     homepage_facet_image_people.jpg, \
                     homepage_facet_image_organizations.jpg, \
                     homepage_facet_image_places.jpg, or \
                     homepage_facet_image_decades.jpg.',
            heading='Featured Topic'
        ),
        FieldPanel('about_the_bmrc')
    ]

    search_fields = Page.search_fields + [
        index.SearchField('introduction'),
        index.SearchField('about_the_bmrc')
    ]

    parent_page_types = [
        'home.HomePage'
    ]

    subpage_types = [
        'portal.CuratedTopicIndexPage',
        'portal.ExhibitIndexPage',
        'standard.StandardPage',
    ]

    max_count = 1

    def get_context(self, request, *args, **kwargs):
        discover_more_facet = random.choice((
            'topics',
            'people',
            'places',
            'organizations',
            'decades'
        ))
        discover_more_facet_uri = 'https://bmrc.lib.uchicago.edu/{}/'.format(
            discover_more_facet
        )
        discover_more_facet_image = Image.objects.get(
            title='homepage_facet_image_{}.jpg'.format(
                discover_more_facet
            )
        )
        collections = get_collections(
            settings.MARKLOGIC_SERVER,
            settings.MARKLOGIC_USERNAME,
            settings.MARKLOGIC_PASSWORD,
            settings.PROXY_SERVER,
            discover_more_facet_uri
        )
        discover_more_topic_uri = random.choice(list(collections.keys()))
        discover_more_topic = \
            urllib.parse.unquote_plus(discover_more_topic_uri).replace(
                'https://bmrc.lib.uchicago.edu/', 
                ''
            ).split('/')[1]
        return {
            **super().get_context(request, *args, **kwargs),
            **{
                'discover_more_facet': discover_more_facet,
                'discover_more_facet_image': discover_more_facet_image,
                'discover_more_facet_uri': discover_more_facet_uri,
                'discover_more_topic': discover_more_topic,
                'discover_more_topic_uri': discover_more_topic_uri
            }
        }

    @property
    def curated_topic_index_page(self):
        """Get curated topic index page."""
        return CuratedTopicIndexPage.objects.first()

    @property
    def exhibit_index_page(self):
        """Get exhibit index page."""
        return ExhibitIndexPage.objects.first()

    @property
    def featured_archive(self):
        """Get featured archive."""
        return Archive.featured_archive

    @property
    def featured_curated_topic(self):
        """Get featured curated topic."""
        return CuratedTopicPage.featured_curated_topic
