# Generated by Django 2.2.7 on 2019-12-03 16:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0003_auto_20191024_2110'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newsstorypage',
            name='excerpt',
            field=models.TextField(blank=True, max_length=300, null=True),
        ),
    ]
