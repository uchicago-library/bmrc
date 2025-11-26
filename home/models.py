from django.core.exceptions import ValidationError
from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import (
    FieldPanel,
    HelpPanel,
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
    page = ParentalKey("home.HomePage", related_name="banner_options")
    banner_option_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    banner_option_title = models.CharField(max_length=100, blank=True, null=True)
    banner_option_text = RichTextField(blank=True, null=True)
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
        FieldPanel("banner_option_image"),
        FieldPanel("banner_option_title"),
        FieldPanel("banner_option_text"),
        PageChooserPanel("button_link"),
        FieldPanel("button_label"),
    ]
    heading = ("Banner Content",)


class AboutSectionShortcut(Orderable):
    """About Section Shortcuts."""
    id = models.AutoField(primary_key=True)
    page = ParentalKey("home.HomePage", related_name="about_section_shortcut")

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
    panels = [
        FieldPanel("small_text"),
        FieldPanel("big_text"),
        FieldPanel("icon_name"),
        PageChooserPanel("link"),
    ]
    heading = ("About Section Button",)


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
            # ("new_row", blocks.NewRow()),
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


    # PROMOTIONAL BANNER
    promo_banner_show = models.BooleanField(
        default=False,
        help_text='Check to display the promotional banner on the home page. At least one image, alt text, and a link are also required to show the banner.'
    )
    promo_banner_desktop_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='Wide banner image for desktop (recommended: 1200px or wider). '
                  'Either desktop or mobile image is required.'
    )
    promo_banner_mobile_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='Square banner image for mobile, around 600px, typically the same used '
                  'for social media. If not provided, the desktop image will be used.'
    )
    promo_banner_alt_text = models.CharField(
        max_length=500,
        blank=True,
        help_text='Describe the image and include ALL text visible in the image '
                  'for accessibility. Screen reader users rely on this description.'
    )
    promo_banner_link_url = models.URLField(
        blank=True,
        help_text='The URL where users will be directed when they click the banner.'
    )


    # HIGHLIGHT SECTION
    highlight_title = RichTextField(
        features=["bold"],  # Restrict to only bold formatting
        blank=True,
        null=True,
        help_text="Title for the banner displayed above the footer. Supports bold text but that makes it blue.",
    )
    highlight_paragraph = models.TextField(
        blank=True,
        null=True,
        help_text="A short paragraph for the banner above the footer.",
    )
    highlight_button_text = models.CharField(
        max_length=100, blank=True, null=True, help_text="Text for the banner button"
    )
    highlight_button_link = models.ForeignKey(
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

    def clean(self):
        """Validate promotional banner fields when enabled."""
        super().clean()
        
        if self.promo_banner_show:
            errors = {}
            
            # Check if at least one image is provided
            if not self.promo_banner_desktop_image and not self.promo_banner_mobile_image:
                errors['promo_banner_desktop_image'] = 'At least one image (desktop or mobile) is required when promotional banner is enabled.'
                errors['promo_banner_mobile_image'] = 'At least one image (desktop or mobile) is required when promotional banner is enabled.'
            
            # Check if alt text is provided
            if not self.promo_banner_alt_text:
                errors['promo_banner_alt_text'] = 'Alt text is required when promotional banner is enabled. Please describe the image and include ALL text visible in it.'
            
            # Check if link URL is provided
            if not self.promo_banner_link_url:
                errors['promo_banner_link_url'] = 'Link URL is required when promotional banner is enabled.'
            
            if errors:
                raise ValidationError(errors)

    # CONTENT PANELS
    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [InlinePanel("banner_options", max_num=3, label="Option")],
            heading="Top Banner Content",
            help_text="If more than one option is set, one is chosen at random to be used for the banner. So every page reload can show a different image, text, title, and button.",
        ),
        MultiFieldPanel(
            [
                FieldPanel("promo_banner_show"),
                FieldPanel("promo_banner_desktop_image"),
                FieldPanel("promo_banner_mobile_image"),
                FieldPanel("promo_banner_alt_text"),
                FieldPanel("promo_banner_link_url"),
            ],
            heading="Promotional Banner",
            help_text="Promotional image banner displayed below alerts and above "
                      "the About section. Useful for campaigns like Giving Tuesday.",
        ),
        MultiFieldPanel(
            [
                FieldPanel("about_title"),
                FieldPanel("about_paragraph"),
                FieldPanel("about_button_text"),
                PageChooserPanel("about_button_link"),
                InlinePanel("about_section_shortcut", max_num=3, label="Shortcut"),
            ],
            heading="About Section with shortcuts",
            help_text="Section below the top banner with a paragraph and shortcuts. Needs a title and text or nothing will be shown. Shortcuts intended to link to Collections(magnifying-glass), Programs(table-columns), Members(building-columns)",
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
            help_text="Intended to highlight the Portal. Needs a title and text or nothing will be shown. ",
        ),
        MultiFieldPanel(
            [
                FieldPanel("banner_title"),
                FieldPanel("banner_paragraph"),
                FieldPanel("banner_button_text"),
                PageChooserPanel("banner_button_link"),
            ],
            heading="Bottom Banner Content",
            help_text="Configure the banner displayed above the footer. This was intended to link to the newsletter signup but can be used for other things. Better to keep it short. Needs a title, text, a button text, and a button link or nothing will be shown. ",
        ),
        FieldPanel("body"),
    ]

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
