import datetime, random, urllib
from . import get_collections
from django import forms
from django.conf import settings
from django.db import models
from django.utils import translation
from django.utils.html import format_html
from django.utils.safestring import mark_safe
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
from wagtail.contrib.table_block.blocks import TableBlock
from wagtail.core.blocks import (
    BooleanBlock, CharBlock, ChoiceBlock, ChooserBlock, FieldBlock, ListBlock,
    PageChooserBlock, RawHTMLBlock, RichTextBlock, StreamBlock, StructBlock,
    TextBlock, TimeBlock, URLBlock
)
from wagtail.core.fields import (
    RichTextField, 
    StreamField,
)
from wagtail.core.models import (
    Orderable, 
    Page
)
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.images.models import Image
from wagtail.search import index
from wagtail.snippets.blocks import SnippetChooserBlock
from wagtailmedia.blocks import AbstractMediaChooserBlock


# Helper functions and constants
BUTTON_CHOICES = (
    ('btn-primary', 'Primary'),
    ('btn-default', 'Secondary'),
    ('btn-reserve', 'Reservation'),
)


# Global streamfield definitions
class AgendaInnerBlock(StructBlock):
    """
    Block definition for the repeatable inner
    portion of the AgendaItem streamfield.
    """
    title = CharBlock(
        required=False, help_text='Talk title, workshop title, etc.'
    )
    presenters = CharBlock(
        required=False,
        help_text='Comma separated list of presenters \
            (if more than one)'
    )
    room_number = CharBlock(required=False)
    description = RichTextBlock(required=False)


class AgendaItemFields(StructBlock):
    """
    Make the AgendaInnerBlock repeatable.
    """
    start_time = TimeBlock(required=False, icon='time')
    end_time = TimeBlock(required=False, icon='time')
    session_title = CharBlock(
        required=False,
        icon='title',
        help_text='Title of the session. \
            Can be used as title of the talk in some situations.'
    )
    event = ListBlock(
        AgendaInnerBlock(),
        icon="edit",
        help_text='A talk or event with a title, presenter \
            room number, and description',
        label=' '
    )


class AnchorTargetBlock(StructBlock):
    """
    Allows authors to add an ID target for Wagtail's anchor link.
    """
    anchor_id_name = CharBlock(max_length=50)

    class Meta:
        icon = 'tag'
        template = 'portal/blocks/anchor_target.html'
        label = 'Anchor link target'


class BlockQuoteBlock(StructBlock):
    """
    Blockquote streamfield block.
    """
    quote = TextBlock('quote title')
    attribution = CharBlock(required=False)

    class Meta:
        icon = 'openquote'
        template = 'portal/blocks/blockquote.html'
 

class ButtonBlock(StructBlock):
    """
    Button streamfield block.
    """
    button_type = ChoiceBlock(
        choices=BUTTON_CHOICES, default=BUTTON_CHOICES[0][0]
    )
    button_text = CharBlock(max_length=20)
    link_external = URLBlock(required=False)
    link_page = PageChooserBlock(required=False)
    link_document = DocumentChooserBlock(required=False)

    class Meta:
        icon = 'plus-inverse'
        template = 'portal/blocks/button.html'


class ClearBlock(StructBlock):
    """
    Allows authors to add a clear between floated elements.
    """

    class Meta:
        icon = 'horizontalrule'
        template = 'portal/blocks/clear.html'


class CodeBlock(StructBlock):
    """
    Code Highlighting Block
    """

    LANGUAGE_CHOICES = (
        ('bash', 'Bash/Shell'),
        ('css', 'CSS'),
        ('html', 'HTML'),
        ('javascript', 'Javascript'),
        ('json', 'JSON'),
        ('ocaml', 'OCaml'),
        ('php5', 'PHP'),
        ('html+php', 'PHP/HTML'),
        ('python', 'Python'),
        ('scss', 'SCSS'),
        ('yaml', 'YAML'),
    )

    language = ChoiceBlock(choices=LANGUAGE_CHOICES)
    code = TextBlock()

    class Meta:
        icon = 'cog'
        label = '_SRC'

    def render(self, value, context=None):
        src = value['code'].strip('\n')
        lang = value['language']

        lexer = get_lexer_by_name(lang)
        formatter = get_formatter_by_name(
            'html',
            linenos=None,
            cssclass='codehilite',
            style='default',
            noclasses=False,
        )
        return mark_safe(highlight(src, lexer, formatter))


class ColumnsBlock(StreamBlock):
    """
    Panel to add columns of rich text. Uses Flex box.
    """
    new_column = RichTextBlock(label="New Column", icon="arrow-right")

    class Meta:
        template = "portal/blocks/columns_block.html"
        icon = "form"
        label = "Text Columns"
        help_text = "Recommend 2-3 columns max"


class ImageFormatChoiceBlock(FieldBlock):
    """
    Alignment options to use with the ImageBlock.
    """
    field = forms.ChoiceField(
        choices=(
            ('pull-left', 'Wrap left'),
            ('pull-right', 'Wrap right'),
            ('fullwidth', 'Full width'),
        )
    )


class ImageBlock(StructBlock):
    """
    Image streamfield block.
    """
    image = ImageChooserBlock()
    title = CharBlock(required=False)
    citation = CharBlock(
        required=False,
        help_text='Photographer, artist, or creator of image',
    )
    caption = TextBlock(
        required=False,
        help_text='Details about or description of image',
    )
    alt_text = CharBlock(
        required=True,
        help_text='Required for ADA compliance',
    )
    alignment = ImageFormatChoiceBlock()
    source = URLBlock(
        required=False,
        help_text='Link to image source (needed for Creative Commons)',
    )
    lightbox = BooleanBlock(
        default=False,
        required=False,
        help_text='Link to a larger version of the image',
    )

    class Meta:
        icon = 'image'
        template = 'portal/blocks/img.html'


class ImageLink(StructBlock):
    """
    Normal image for web exhibits.
    """
    image = ImageChooserBlock(required=False)
    alt_text = CharBlock(
        required=False,
        help_text='Required if no link text supplied for ADA compliance',
    )
    icon = CharBlock(
        required=False,
        help_text="Font Awesome icon name if you're not using an image"
    )
    link_text = CharBlock(
        required=False,
        help_text='Text to display below the image or icon',
    )
    link_external = URLBlock(required=False)
    link_page = PageChooserBlock(required=False)
    link_document = DocumentChooserBlock(required=False)

    class Meta:
        icon = 'image'
        template = 'portal/blocks/image_link.html'


class LocalMediaBlock(AbstractMediaChooserBlock):

    def render_basic(self, value, context=None):
        if not value:
            return ''

        if value.type == 'video':
            player_code = '''
            <div>
                <video width="320" height="240" controls>
                    <source src="{0}" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
            </div>
            '''
        else:
            player_code = '''
            <div>
                <audio controls>
                    <source src="{0}" type="audio/mpeg">
                    Your browser does not support the audio element.
                </audio>
            </div>
            '''

        return format_html(player_code, value.file.url)

    class Meta:
        icon = 'media'


class ParagraphBlock(StructBlock):
    """
    Paragraph streamfield block.
    """
    paragraph = RichTextBlock()

    class Meta:
        icon = 'pilcrow'
        form_classname = 'paragraph-block struct-block'
        template = 'portal/blocks/paragraph.html'


class PullQuoteBlock(StructBlock):
    """
    Pullquote streamfield block.
    """
    quote = RichTextBlock()

    class Meta:
        icon = 'arrow-left'
        template = 'portal/blocks/pullquote.html'


class SoloImage(StructBlock):
    """
    Normal image for web exhibits.
    """
    image = ImageChooserBlock()
    citation = RichTextBlock(blank=True, null=True, required=False)
    caption = RichTextBlock(blank=True, null=True, required=False)
    alt_text = CharBlock(
        required=False,
        help_text=
        'Required for ADA compliance if no caption or citation is provided',
    )

    class Meta:
        icon = 'image'
        template = 'portal/blocks/solo_img.html'


class DuoImage(StructBlock):
    """
    Panel of two images stacked side
    by side. Used in web exhibits.
    """
    image_one = SoloImage(
        help_text='First of two images displayed \
            side by side'
    )
    image_two = SoloImage(
        help_text='Second of two images displayed \
            side by side'
    )

    class Meta:
        icon = 'image'
        template = 'portal/blocks/duo_img.html'


class ExhibitBodyFields(StreamBlock):
    """
    Standard default streamfield options to be shared
    across content types.
    """
    paragraph = ParagraphBlock(group="Format and Text")
    h2 = CharBlock(
        icon='title',
        classname='title',
        template='portal/blocks/h2.html',
        group='Format and Text'
    )
    h3 = CharBlock(
        icon='title',
        classname='title',
        template='portal/blocks/h3.html',
        group='Format and Text'
    )
    h4 = CharBlock(
        icon='title',
        classname='title',
        template='portal/blocks/h4.html',
        group='Format and Text'
    )
    h5 = CharBlock(
        icon='title',
        classname='title',
        template='portal/blocks/h5.html',
        group='Format and Text'
    )
    columns_block = ColumnsBlock(group='Format and Text')
    blockquote = BlockQuoteBlock(group='Format and Text')
    pullquote = PullQuoteBlock(group='Format and Text')
    image = ImageBlock(label='Image', group="Images and Media")
    solo_image = SoloImage(
        help_text='Single image with caption on the right',
        group="Images and Media"
    )
    duo_image = DuoImage(
        help_text='Two images side by side with captions below',
        group="Images and Media"
    )
    local_media = LocalMediaBlock(
        label="Video or Audio",
        help_text='Audio or video files that have been uploaded into Wagtail',
        group="Images and Media"
    )
    video = EmbedBlock(
        icon='media',
        label='External Video Embed',
        help_text='Embed video that is hosted on YouTube or Vimeo',
        group="Images and Media"
    )
    button = ButtonBlock(group="Links")
    image_link = ImageLink(
        label="Linked Image",
        help_text='A fancy link made out of a thumbnail and simple text',
        group="Links"
    )
    anchor_target = AnchorTargetBlock(
        help_text=
        'Where you want an anchor link to jump to. Must exactly match the "#" label supplied in anchor link (found in Paragraph streamfield).',
        group="Links"
    )

    # Begin TableBlock Setup
    language = translation.get_language()
    if language is not None and len(language) > 2:
        language = language[:2]

    options = {
        'minSpareRows': 0,
        'startRows': 3,
        'startCols': 3,
        'colHeaders': False,
        'rowHeaders': False,
        'contextMenu': True,
        'editor': 'text',
        'stretchH': 'all',
        'height': 108,
        'language': language,
        'renderer': 'html',
        'autoColumnSize': False,
    }
    table = TableBlock(
        table_options=options,
        template='portal/blocks/table.html',
        help_text='Right + click in a table cell for more options. \
Use <em>text</em> for italics, <strong>text</strong> for bold, and \
<a href="https://duckduckgo.com">text</a> for links.',
        group="Layout and Data"
    )
    agenda_item = AgendaItemFields(
        icon='date',
        template='portal/blocks/agenda.html',
        group="Layout and Data"
    )
    clear = ClearBlock(
        lable="Clear Formatting",
        help_text='Resets layout before or after floated images.',
        group="Layout and Data"
    )
    code = CodeBlock(group="Layout and Data")
    html = RawHTMLBlock(
        help_text='Display code as text for tutorial or documentation purposes',
        group="Layout and Data"
    )

    class Meta:
        required = False


# JEJ


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
        month_number += 4
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

    body = StreamField(ExhibitBodyFields(), blank=True, null=True)

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
        'portal.ExhibitIndexPage'
    ]

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
