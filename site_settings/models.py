from django.db import models

from wagtail.admin.panels import FieldPanel, HelpPanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.fields import RichTextField


@register_setting
class FooterSettings(BaseSiteSetting):
    """Social media settings for our custom website."""

    id = models.AutoField(primary_key=True)
    facebook = models.URLField(blank=True, null=True, help_text="Facebook URL")
    twitter = models.URLField(blank=True, null=True, help_text="Twitter URL")
    instagram = models.URLField(blank=True,
                                null=True,
                                help_text="Instagram profile URL")
    address = RichTextField(blank=True, null=True, help_text="Mailing address")

    panels = [
        MultiFieldPanel([
            FieldPanel("facebook"),
            FieldPanel("twitter"),
            FieldPanel("instagram"),
            FieldPanel("address"),
        ],
                        heading="Footer Settings")
    ]


@register_setting
class AlertBanner(BaseSiteSetting):
    """Create and toggle a site-wide alert banner."""

    INFO = 'alert-info'
    LOW = 'alert-low'
    HIGH = 'alert-high'
    ALERT_TYPES = (
        (INFO, 'Informational Alert'),
        (LOW, 'General Alert'),
        (HIGH, 'Critical Alert'),
    )

    id = models.AutoField(primary_key=True)
    enable = models.BooleanField(
        default=False,
        help_text='Checking this box will enable the alert on all web pages.')
    alert_message = RichTextField(blank=True,
                                  null=True,
                                  help_text="Alert Message")
    alert_level = models.CharField(
        max_length=25,
        choices=ALERT_TYPES,
        default=INFO,
    )

    panels = [
        MultiFieldPanel([
            FieldPanel("enable"),
            FieldPanel("alert_message"),
            FieldPanel("alert_level"),
        ],
                        heading="Alert Banner")
    ]


@register_setting
class PromoBanner(BaseSiteSetting):
    """Create and toggle a promotional image banner on the home page."""

    id = models.AutoField(primary_key=True)
    enable = models.BooleanField(
        default=False,
        help_text='Checking this box will enable the promotional banner on the home page.')
    desktop_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='The banner image for desktop displays. '
                  'Recommended width: 1200px or wider.'
    )
    mobile_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='Optional banner image optimized for mobile displays. '
                  'If not provided, the desktop image will be used. '
                  'Recommended width: 600px.'
    )
    alt_text = models.CharField(
        max_length=500,
        blank=True,
        help_text='Required for accessibility. Describe the image and include '
                  'ALL text visible in the image. This helps screen reader '
                  'users understand the promotional content.'
    )
    link_url = models.URLField(
        blank=True,
        help_text='Required. The URL where users will be directed when '
                  'they click the banner.'
    )

    panels = [
        MultiFieldPanel([
            HelpPanel(content='''
                <div style="background-color: #f0f4f8; padding: 15px;
                     border-radius: 5px; margin-bottom: 15px;">
                    <h3 style="margin-top: 0;">Promotional Banner Guidelines</h3>
                    <p>This banner appears at the top of the home page,
                       below any alert messages and above the About section.</p>
                    <ul>
                        <li><strong>Desktop Image:</strong> Upload a wide banner
                            image (recommended: 1200px or wider).</li>
                        <li><strong>Mobile Image:</strong> Optional - upload a
                            smaller or differently cropped version for mobile
                            devices.</li>
                        <li><strong>Alt Text:</strong> IMPORTANT - Include ALL
                            text that appears in the image for accessibility.
                            Screen reader users rely on this description.</li>
                        <li><strong>Link URL:</strong> The destination page when
                            users click the banner.</li>
                    </ul>
                </div>
            '''),
            FieldPanel("enable"),
            FieldPanel("desktop_image"),
            FieldPanel("mobile_image"),
            FieldPanel("alt_text"),
            FieldPanel("link_url"),
        ],
                        heading="Promotional Banner")
    ]
