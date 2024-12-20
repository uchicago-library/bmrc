# Generated by Django 2.2.9 on 2020-01-18 10:27

from django.db import migrations, models
import django.db.models.deletion
import streams.blocks
import wagtail.blocks
import wagtail.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0041_group_collection_permissions_verbose_name_plural'),
        ('news', '0005_newssidebar'),
    ]

    operations = [
        migrations.CreateModel(
            name='NewsletterSignupPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
                ('body', wagtail.fields.StreamField([('richtext', streams.blocks.RichtextBlock()), ('webfeed', wagtail.blocks.StructBlock([('webfeed_title', wagtail.blocks.CharBlock(help_text='Title for callout section', required=False)), ('webfeed_code', wagtail.blocks.RawHTMLBlock(required=False))])), ('image_block', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('caption', streams.blocks.RichtextBlock(features=['bold', 'italic', 'link'], label='Caption', required=False)), ('alignment', streams.blocks.ImageFormatChoiceBlock(required=False))])), ('new_row', wagtail.blocks.StructBlock([]))], blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Newsletter Form',
                'verbose_name_plural': 'Newsletter Forms',
            },
            bases=('wagtailcore.page',),
        ),
    ]
