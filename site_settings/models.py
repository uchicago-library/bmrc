from django.db import models

from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseSetting, register_setting
from wagtail.core.fields import RichTextField


@register_setting
class FooterSettings(BaseSetting):
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
class AlertBanner(BaseSetting):
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
