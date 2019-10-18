# Generated by Django 2.2.6 on 2019-10-18 20:51

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields
import streams.blocks
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailimages', '0001_squashed_0021'),
        ('wagtailcore', '0041_group_collection_permissions_verbose_name_plural'),
        ('home', '0002_create_homepage'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='homepage',
            options={'verbose_name': 'Home Page', 'verbose_name_plural': 'Home Pages'},
        ),
        migrations.AddField(
            model_name='homepage',
            name='body',
            field=wagtail.core.fields.StreamField([('richtext', streams.blocks.RichtextBlock())], blank=True, null=True),
        ),
        migrations.CreateModel(
            name='HomePageCarouselImages',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('carousel_title', models.CharField(blank=True, max_length=100, null=True)),
                ('carousel_text', wagtail.core.fields.RichTextField(blank=True, null=True)),
                ('carousel_button', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailcore.Page')),
                ('carousel_image', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.Image')),
                ('page', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='carousel_images', to='home.HomePage')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
    ]
