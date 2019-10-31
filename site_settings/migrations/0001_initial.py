# Generated by Django 2.2.6 on 2019-10-24 23:05

from django.db import migrations, models
import django.db.models.deletion
import wagtail.core.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('wagtailcore', '0041_group_collection_permissions_verbose_name_plural'),
    ]

    operations = [
        migrations.CreateModel(
            name='FooterSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('facebook', models.URLField(blank=True, help_text='Facebook URL', null=True)),
                ('twitter', models.URLField(blank=True, help_text='Twitter URL', null=True)),
                ('instagram', models.URLField(blank=True, help_text='Instagram profile URL', null=True)),
                ('address', wagtail.core.fields.RichTextField(blank=True, help_text='Mailing address', null=True)),
                ('site', models.OneToOneField(editable=False, on_delete=django.db.models.deletion.CASCADE, to='wagtailcore.Site')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]