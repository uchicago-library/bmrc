# Generated by Django 2.2.7 on 2019-12-04 13:56

from django.db import migrations
import streams.blocks
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('memb_collections', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='membcollectionindexpage',
            name='body',
            field=wagtail.core.fields.StreamField([('richtext', streams.blocks.RichtextBlock()), ('image_block', wagtail.core.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('caption', streams.blocks.RichtextBlock(features=['bold', 'italic', 'link'], label='Caption', required=False)), ('alignment', streams.blocks.ImageFormatChoiceBlock(required=False))])), ('new_row', wagtail.core.blocks.StructBlock([])), ('memb_coll_search_block', wagtail.core.blocks.StructBlock([('label', wagtail.core.blocks.CharBlock(help_text='Optional: Label placed above search box', required=False)), ('search_help_text', wagtail.core.blocks.CharBlock(help_text='Optional: Placed below search box', required=False))]))], blank=True, null=True),
        ),
    ]
