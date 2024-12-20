# Generated by Django 2.2.6 on 2019-10-23 20:22

from django.db import migrations
import streams.blocks
import wagtail.blocks
import wagtail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0005_auto_20191022_1953'),
    ]

    operations = [
        migrations.AlterField(
            model_name='homepage',
            name='body',
            field=wagtail.fields.StreamField([('richtext', streams.blocks.RichtextBlock()), ('page_callout', wagtail.blocks.StructBlock([('callout_title', wagtail.blocks.CharBlock(help_text='Title for callout section', required=False)), ('callout_text', streams.blocks.RichtextBlock(features=['bold', 'italic', 'ol', 'ul', 'link', 'document-link'], label='Callout Text', required=False)), ('button_link', wagtail.blocks.PageChooserBlock(help_text='Where you want the button to go', required=False)), ('button_label', wagtail.blocks.CharBlock(help_text='Text that shows up in button', required=False))])), ('webfeed', wagtail.blocks.StructBlock([('webfeed_title', wagtail.blocks.CharBlock(help_text='Title for callout section', required=False)), ('webfeed_code', wagtail.blocks.RawHTMLBlock(required=False))])), ('new_row', wagtail.blocks.StructBlock([]))], blank=True, null=True),
        ),
    ]
