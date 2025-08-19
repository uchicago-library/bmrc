from base.models import AbstractBasePage
from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page


class ProgramPage(AbstractBasePage):
    excerpt = RichTextField(
        blank=True,
        features=['bold', 'italic', 'link'],
        help_text='Short description to display on the programs listing page. If not set, the content body is truncated.',
    )

    thumbnail = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='Image to display for the program. Alt text is defined when editing the image itself.',
    )

    current = models.BooleanField(
        default=True,
        help_text='Whether or not the program is currently active.',
    )

    content_panels = AbstractBasePage.content_panels + [
        FieldPanel('excerpt'),
        FieldPanel('thumbnail'),
        FieldPanel('current'),
    ]


class ProgramsListingPage(Page):
    subpage_types = ['programs.ProgramPage']

    def get_context(self, request):
        context = super().get_context(request)

        current_programs = (
            ProgramPage.objects.child_of(self).live().filter(current=True)
        )

        past_programs = ProgramPage.objects.child_of(self).live().filter(current=False)

        context['current_programs'] = current_programs
        context['past_programs'] = past_programs

        return context
