# Generated by Django 3.2.11 on 2022-01-21 16:29

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields
import streams.blocks
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0066_collection_management_permissions'),
        ('wagtailimages', '0023_add_choose_permissions'),
        ('portal', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PortalStandardPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.page')),
                ('body', wagtail.core.fields.StreamField([('richtext', streams.blocks.RichtextBlock(group='Format and Text')), ('two_column_block', wagtail.core.blocks.StreamBlock([('new_column', streams.blocks.RichtextBlock(icon='arrow-right', label='New Column'))], group='Format and Text')), ('info_box_block', wagtail.core.blocks.StructBlock([('text', streams.blocks.RichtextBlock(features=['h2', 'h3', 'bold', 'ol', 'ul', 'hr', 'italic', 'link', 'document-link'], label='Featured Text', required=True)), ('style_type', streams.blocks.InfoBoxStyleChoiceBlock(required=True))], group='Format and Text')), ('footnote_block', wagtail.core.blocks.StructBlock([('text', streams.blocks.RichtextBlock(features=['bold', 'ol', 'ul', 'italic', 'link', 'document-link'], label='Footnote Text', required=False))], group='Format and Text')), ('image_block', wagtail.core.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('caption', streams.blocks.RichtextBlock(features=['bold', 'italic', 'link'], label='Caption', required=False)), ('alignment', streams.blocks.ImageFormatChoiceBlock(required=False))], group='Layout and Images')), ('fellows_block', wagtail.core.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(label='Profile Photo', required=False)), ('profile_text', streams.blocks.RichtextBlock(features=['h2', 'h3', 'bold', 'italic', 'link'], label='Profile Text', required=False))], group='Layout and Images')), ('clear_block', streams.blocks.ClearBlock(group='Layout and Images')), ('webfeed', wagtail.core.blocks.StructBlock([('webfeed_title', wagtail.core.blocks.CharBlock(help_text='Title for callout section', required=False)), ('webfeed_code', wagtail.core.blocks.RawHTMLBlock(required=False))], group='Layout and Images'))], blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.AlterField(
            model_name='exhibitpage',
            name='image',
            field=models.ForeignKey(blank=True, help_text='A small version of this image will display on the portal                    homepage. It does NOT appear on the ExhibitPage itself.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.image'),
        ),
        migrations.CreateModel(
            name='PortalStandardSideBar',
            fields=[
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('sidebar_title', models.CharField(blank=True, max_length=100, null=True)),
                ('sidebar_text', wagtail.core.fields.RichTextField(blank=True, null=True)),
                ('page', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='sidebar', to='portal.portalstandardpage')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
    ]
