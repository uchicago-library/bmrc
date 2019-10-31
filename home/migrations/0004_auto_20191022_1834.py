# Generated by Django 2.2.6 on 2019-10-22 18:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0003_auto_20191018_2051'),
    ]

    operations = [
        migrations.AddField(
            model_name='homepagecarouselimages',
            name='button_label',
            field=models.CharField(blank=True, help_text='Text that shows up in button', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='homepagecarouselimages',
            name='carousel_button',
            field=models.ForeignKey(blank=True, help_text='Where you want the button to go', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailcore.Page'),
        ),
    ]