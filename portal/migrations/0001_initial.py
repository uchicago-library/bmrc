# Generated by Django 3.2.11 on 2022-01-19 20:49

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields
import streams.blocks
import wagtail.blocks
import wagtail.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('wagtailimages', '0023_add_choose_permissions'),
        ('wagtailcore', '0066_collection_management_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='CuratedTopicIndexPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.page')),
                ('body', wagtail.fields.StreamField([('richtext', streams.blocks.RichtextBlock(group='Format and Text')), ('two_column_block', wagtail.blocks.StreamBlock([('new_column', streams.blocks.RichtextBlock(icon='arrow-right', label='New Column'))], group='Format and Text')), ('info_box_block', wagtail.blocks.StructBlock([('text', streams.blocks.RichtextBlock(features=['h2', 'h3', 'bold', 'ol', 'ul', 'hr', 'italic', 'link', 'document-link'], label='Featured Text', required=True)), ('style_type', streams.blocks.InfoBoxStyleChoiceBlock(required=True))], group='Format and Text')), ('footnote_block', wagtail.blocks.StructBlock([('text', streams.blocks.RichtextBlock(features=['bold', 'ol', 'ul', 'italic', 'link', 'document-link'], label='Footnote Text', required=False))], group='Format and Text')), ('image_block', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('caption', streams.blocks.RichtextBlock(features=['bold', 'italic', 'link'], label='Caption', required=False)), ('alignment', streams.blocks.ImageFormatChoiceBlock(required=False))], group='Layout and Images')), ('fellows_block', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(label='Profile Photo', required=False)), ('profile_text', streams.blocks.RichtextBlock(features=['h2', 'h3', 'bold', 'italic', 'link'], label='Profile Text', required=False))], group='Layout and Images')), ('clear_block', streams.blocks.ClearBlock(group='Layout and Images')), ('webfeed', wagtail.blocks.StructBlock([('webfeed_title', wagtail.blocks.CharBlock(help_text='Title for callout section', required=False)), ('webfeed_code', wagtail.blocks.RawHTMLBlock(required=False))], group='Layout and Images'))], blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='ExhibitIndexPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.page')),
                ('body', wagtail.fields.StreamField([('richtext', streams.blocks.RichtextBlock(group='Format and Text')), ('two_column_block', wagtail.blocks.StreamBlock([('new_column', streams.blocks.RichtextBlock(icon='arrow-right', label='New Column'))], group='Format and Text')), ('info_box_block', wagtail.blocks.StructBlock([('text', streams.blocks.RichtextBlock(features=['h2', 'h3', 'bold', 'ol', 'ul', 'hr', 'italic', 'link', 'document-link'], label='Featured Text', required=True)), ('style_type', streams.blocks.InfoBoxStyleChoiceBlock(required=True))], group='Format and Text')), ('footnote_block', wagtail.blocks.StructBlock([('text', streams.blocks.RichtextBlock(features=['bold', 'ol', 'ul', 'italic', 'link', 'document-link'], label='Footnote Text', required=False))], group='Format and Text')), ('image_block', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('caption', streams.blocks.RichtextBlock(features=['bold', 'italic', 'link'], label='Caption', required=False)), ('alignment', streams.blocks.ImageFormatChoiceBlock(required=False))], group='Layout and Images')), ('fellows_block', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(label='Profile Photo', required=False)), ('profile_text', streams.blocks.RichtextBlock(features=['h2', 'h3', 'bold', 'italic', 'link'], label='Profile Text', required=False))], group='Layout and Images')), ('clear_block', streams.blocks.ClearBlock(group='Layout and Images')), ('webfeed', wagtail.blocks.StructBlock([('webfeed_title', wagtail.blocks.CharBlock(help_text='Title for callout section', required=False)), ('webfeed_code', wagtail.blocks.RawHTMLBlock(required=False))], group='Layout and Images'))], blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='ExhibitPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.page')),
                ('body', wagtail.fields.StreamField([('richtext', streams.blocks.RichtextBlock(group='Format and Text')), ('two_column_block', wagtail.blocks.StreamBlock([('new_column', streams.blocks.RichtextBlock(icon='arrow-right', label='New Column'))], group='Format and Text')), ('info_box_block', wagtail.blocks.StructBlock([('text', streams.blocks.RichtextBlock(features=['h2', 'h3', 'bold', 'ol', 'ul', 'hr', 'italic', 'link', 'document-link'], label='Featured Text', required=True)), ('style_type', streams.blocks.InfoBoxStyleChoiceBlock(required=True))], group='Format and Text')), ('footnote_block', wagtail.blocks.StructBlock([('text', streams.blocks.RichtextBlock(features=['bold', 'ol', 'ul', 'italic', 'link', 'document-link'], label='Footnote Text', required=False))], group='Format and Text')), ('image_block', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('caption', streams.blocks.RichtextBlock(features=['bold', 'italic', 'link'], label='Caption', required=False)), ('alignment', streams.blocks.ImageFormatChoiceBlock(required=False))], group='Layout and Images')), ('fellows_block', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(label='Profile Photo', required=False)), ('profile_text', streams.blocks.RichtextBlock(features=['h2', 'h3', 'bold', 'italic', 'link'], label='Profile Text', required=False))], group='Layout and Images')), ('clear_block', streams.blocks.ClearBlock(group='Layout and Images')), ('webfeed', wagtail.blocks.StructBlock([('webfeed_title', wagtail.blocks.CharBlock(help_text='Title for callout section', required=False)), ('webfeed_code', wagtail.blocks.RawHTMLBlock(required=False))], group='Layout and Images'))], blank=True, null=True)),
                ('image', models.ForeignKey(blank=True, help_text='A small version of this image will display on the portal                    homepage. It does NOT appera on the ExhibitPage itself.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.image')),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='PortalHomePage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.page')),
                ('introduction', wagtail.fields.RichTextField(blank=True, null=True)),
                ('about_the_bmrc', wagtail.fields.RichTextField(blank=True, null=True)),
                ('featured_exhibit', models.ForeignKey(blank=True, help_text='Choose which exhibit to highlight.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='portal.exhibitpage')),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='ExhibitPageSideBar',
            fields=[
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('sidebar_title', models.CharField(blank=True, max_length=100, null=True)),
                ('sidebar_text', wagtail.fields.RichTextField(blank=True, null=True)),
                ('page', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='sidebar', to='portal.exhibitpage')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ExhibitIndexSideBar',
            fields=[
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('sidebar_title', models.CharField(blank=True, max_length=100, null=True)),
                ('sidebar_text', wagtail.fields.RichTextField(blank=True, null=True)),
                ('page', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='sidebar', to='portal.exhibitindexpage')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CuratedTopicPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.page')),
                ('caption', models.CharField(blank=True, help_text='Displays underneath the image on the curated topic page                    and as alt text.', max_length=400)),
                ('body', wagtail.fields.RichTextField(blank=True, null=True)),
                ('byline', models.CharField(blank=True, help_text='Author name, appears below the body.', max_length=200)),
                ('search_url', models.URLField(max_length=2000)),
                ('bottom_text', wagtail.fields.RichTextField(blank=True, null=True)),
                ('image', models.ForeignKey(blank=True, help_text='A small version of this image will display on the portal                    homepage, and a large version will display at the top of                    each curated topic page.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.image')),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='CuratedTopicIndexSideBar',
            fields=[
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('sidebar_title', models.CharField(blank=True, max_length=100, null=True)),
                ('sidebar_text', wagtail.fields.RichTextField(blank=True, null=True)),
                ('page', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='sidebar', to='portal.curatedtopicindexpage')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Archive',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Archive name.', max_length=200)),
                ('address', models.CharField(blank=True, help_text='Street address.', max_length=400)),
                ('link', wagtail.fields.RichTextField(blank=True, help_text='Link back to archive homepage, contact page, or other informational page.', max_length=2000)),
                ('spotlight', wagtail.fields.RichTextField(blank=True, help_text='Spotlight text for the portal homepage.')),
                ('finding_aid_prefix', models.CharField(help_text='Prefix that associates specific EAD filenames with this archive, in the form "BMRC.<ARCHIVE-NAME>"', max_length=200)),
                ('is_member', models.BooleanField(default=True, help_text='Member archives will be included in the portal homepage rotation.')),
                ('order', models.IntegerField(default=1000, help_text='Choose the order this archive should appear in when featured on the portal homepage.')),
                ('logo', models.ForeignKey(blank=True, help_text='archive logo.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.image')),
            ],
        ),
    ]
