# Generated by Django 3.2.11 on 2022-01-18 20:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0007_auto_20200820_2135'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newssidebar',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]