# Generated by Django 2.2.6 on 2019-10-23 23:22

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields
import streams.blocks
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('standard', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='standardpage',
            name='body',
            field=wagtail.core.fields.StreamField([('richtext', streams.blocks.RichtextBlock()), ('page_callout', wagtail.core.blocks.StructBlock([('callout_title', wagtail.core.blocks.CharBlock(help_text='Title for callout section', required=False)), ('callout_text', streams.blocks.RichtextBlock(features=['bold', 'italic', 'ol', 'ul', 'link', 'document-link'], label='Callout Text', required=False)), ('button_link', wagtail.core.blocks.PageChooserBlock(help_text='Where you want the button to go', required=False)), ('button_label', wagtail.core.blocks.CharBlock(help_text='Text that shows up in button', required=False))])), ('image_block', wagtail.core.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('caption', streams.blocks.RichtextBlock(features=['bold', 'italic', 'link'], label='Caption', required=False)), ('alignment', streams.blocks.ImageFormatChoiceBlock(required=False))])), ('new_row', wagtail.core.blocks.StructBlock([]))], blank=True, null=True),
        ),
        migrations.CreateModel(
            name='SideBar',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('sidebar_title', models.CharField(blank=True, max_length=100, null=True)),
                ('sidebar_text', wagtail.core.fields.RichTextField(blank=True, null=True)),
                ('page', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='sidebar', to='standard.StandardPage')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
    ]