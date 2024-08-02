# Generated by Django 2.2.9 on 2020-01-18 02:43

from django.db import migrations
import streams.blocks
import wagtail.blocks
import wagtail.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('standard', '0004_auto_20200117_2147'),
    ]

    operations = [
        migrations.AlterField(
            model_name='standardpage',
            name='body',
            field=wagtail.fields.StreamField([('richtext', streams.blocks.RichtextBlock()), ('image_block', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('caption', streams.blocks.RichtextBlock(features=['bold', 'italic', 'link'], label='Caption', required=False)), ('alignment', streams.blocks.ImageFormatChoiceBlock(required=False))])), ('page_callout', wagtail.blocks.StructBlock([('callout_title', wagtail.blocks.CharBlock(help_text='Title for callout section', required=False)), ('callout_text', streams.blocks.RichtextBlock(features=['bold', 'italic', 'ol', 'ul', 'link', 'document-link'], label='Callout Text', required=False)), ('button_link', wagtail.blocks.PageChooserBlock(help_text='Where you want the button to go', required=False)), ('button_label', wagtail.blocks.CharBlock(help_text='Text that shows up in button', required=False))])), ('fellows_block', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(label='Profile Photo', required=False)), ('profile_text', streams.blocks.RichtextBlock(features=['h2', 'h3', 'bold', 'italic', 'link'], label='Profile Text', required=False))]))], blank=True, null=True),
        ),
    ]
