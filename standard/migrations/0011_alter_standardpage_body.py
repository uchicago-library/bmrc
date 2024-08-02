# Generated by Django 3.2.15 on 2023-10-05 18:59

import django.core.validators
from django.db import migrations
import re
import streams.blocks
import wagtail.blocks
import wagtail.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('standard', '0010_alter_standardpage_body'),
    ]

    operations = [
        migrations.AlterField(
            model_name='standardpage',
            name='body',
            field=wagtail.fields.StreamField([('richtext', streams.blocks.RichtextBlock(group='Format and Text')), ('two_column_block', wagtail.blocks.StreamBlock([('new_column', streams.blocks.RichtextBlock(icon='arrow-right', label='New Column'))], group='Format and Text')), ('info_box_block', wagtail.blocks.StructBlock([('text', streams.blocks.RichtextBlock(features=['h2', 'h3', 'bold', 'ol', 'ul', 'hr', 'italic', 'link', 'document-link'], label='Featured Text', required=True)), ('style_type', streams.blocks.InfoBoxStyleChoiceBlock(required=True))], group='Format and Text')), ('footnote_block', wagtail.blocks.StructBlock([('text', streams.blocks.RichtextBlock(features=['bold', 'ol', 'ul', 'italic', 'link', 'document-link'], label='Footnote Text', required=False))], group='Format and Text')), ('image_block', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('caption', streams.blocks.RichtextBlock(features=['bold', 'italic', 'link'], label='Caption', required=False)), ('alignment', streams.blocks.ImageFormatChoiceBlock(required=False))], group='Layout and Images')), ('fellows_block', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(label='Profile Photo', required=False)), ('profile_text', streams.blocks.RichtextBlock(features=['h2', 'h3', 'bold', 'italic', 'link'], label='Profile Text', required=False)), ('size', wagtail.blocks.ChoiceBlock(choices=[('LG', 'Large'), ('MD', 'Medium'), ('SM', 'Small')])), ('anchor', wagtail.blocks.CharBlock(help_text='Slug for anchor link', max_length=50, required=False, validators=[django.core.validators.RegexValidator(re.compile('^[-a-zA-Z0-9_]+\\Z'), 'Enter a valid “slug” consisting of letters, numbers, underscores or hyphens.', 'invalid')]))], group='Layout and Images')), ('clear_block', streams.blocks.ClearBlock(group='Layout and Images')), ('webfeed', wagtail.blocks.StructBlock([('webfeed_title', wagtail.blocks.CharBlock(help_text='Title for callout section', required=False)), ('webfeed_code', wagtail.blocks.RawHTMLBlock(required=False))], group='Layout and Images'))], blank=True, null=True),
        ),
    ]
