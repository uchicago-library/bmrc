from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    PageChooserPanel,
)
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Orderable, Page

from news.models import NewsStoryPage
from streams import blocks


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
    button_label = models.CharField(
        max_length=100, null=True, blank=True, help_text='Text that shows up in button'
    )

    panels = [
        FieldPanel("carousel_image"),
        FieldPanel("carousel_title"),
        FieldPanel("carousel_text"),
        PageChooserPanel("button_link"),
        FieldPanel("button_label"),
    ]
    heading = ("Banner Content",)


class AboutSectionButton(models.Model):
    """Reusable model for About Section buttons."""
    small_text = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Small text for the button in the About Section.",
    )
    big_text = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Big text for the button in the About Section.",
    )
    icon_name = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Icon name for the button in the About Section.",
    )
    link = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Link for the button in the About Section.",
    )

    class Meta:
        abstract = True


class HomePage(Page):
    """Home page model"""

    template = "home/home_page.html"
    max_count = 1
    parent_page_type = ['wagtailcore.Page']

    body = StreamField(
        [
            ("richtext", blocks.RichtextBlock()),
            ("page_callout", blocks.PageCallout()),
            ("webfeed", blocks.WebFeedBlock()),
            ("new_row", blocks.NewRow()),
        ],
        null=True,
        blank=True,
        help_text="Main content area of the home page. Add various types of blocks here. It is advisable to keep short form content here, possibly linking to longer content elsewhere, like a news story.",
    )

    # ABOUT SECTION
    about_title = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Title for the banner displayed above the footer.",
    )
    about_paragraph = models.TextField(
        blank=True,
        null=True,
        help_text="A short paragraph for the banner above the footer.",
    )
    about_button_text = models.CharField(
        max_length=100, blank=True, null=True, help_text="Text for the banner button"
    )
    about_button_link = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Page to which the banner button will link.",
    )

    # ABOUT SECTION BUTTONS
    about_button_1 = models.OneToOneField(
        AboutSectionButton,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="First button in the About Section.",
    )
    about_button_2 = models.OneToOneField(
        AboutSectionButton,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Second button in the About Section.",
    )
    about_button_3 = models.OneToOneField(
        AboutSectionButton,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Third button in the About Section.",
    )

    # HIGHLIGHT SECTION
    highglight_title = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Title for the banner displayed above the footer.",
    )
    highglight_paragraph = models.TextField(
        blank=True,
        null=True,
        help_text="A short paragraph for the banner above the footer.",
    )
    highglight_button_text = models.CharField(
        max_length=100, blank=True, null=True, help_text="Text for the banner button"
    )
    highglight_button_link = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Page to which the banner button will link.",
    )
    highlight_background = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Image for the Highlight Section.",
    )

    # BOTTOM BANNER
    banner_title = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Title for the banner displayed above the footer.",
    )
    banner_paragraph = models.TextField(
        blank=True,
        null=True,
        help_text="A short paragraph for the banner above the footer.",
    )
    banner_button_text = models.CharField(
        max_length=100, blank=True, null=True, help_text="Text for the banner button"
    )
    banner_button_link = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Page to which the banner button will link.",
    )

    # CONTENT PANELS
    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [InlinePanel("carousel_images", max_num=3, label="Image")],
            heading="Top Banner Content",
            help_text="If more than one image is set, one is chosen at random to be used for the banner and the respective text and link is included in the banner. So every page reload might can a different image with the respective content.",
        ),
        MultiFieldPanel(
            [
                FieldPanel("about_title"),
                FieldPanel("about_paragraph"),
                FieldPanel("about_button_text"),
                PageChooserPanel("about_button_link"),
                FieldPanel("about_button_1"),
                FieldPanel("about_button_2"),
                FieldPanel("about_button_3"),
            ],
            heading="About Section with shortcuts",
            help_text="Section with a paragraph and shortcuts below the top banner. Shortcuts to Collections, Programs, Members",
        ),
        MultiFieldPanel(
            [
                FieldPanel("highlight_title"),
                FieldPanel("highlight_paragraph"),
                FieldPanel("highlight_button_text"),
                PageChooserPanel("highlight_button_link"),
                FieldPanel("highlight_background"),
            ],
            heading="Highlight Section",
            help_text="Intended to highlight the Portal.",
        ),
        MultiFieldPanel(
            [
                FieldPanel("banner_title"),
                FieldPanel("banner_paragraph"),
                FieldPanel("banner_button_text"),
                PageChooserPanel("banner_button_link"),
            ],
            heading="Bottom Banner Content",
            help_text="Configure the banner displayed above the footer. This was intended to link to the newsletter signup but can be used for other things. Better to keep it short.",
        ),
        FieldPanel("body"),
    ]
    self.about_buttons = [self.about_button_1, self.about_button_2, self.about_button_3]
    
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
