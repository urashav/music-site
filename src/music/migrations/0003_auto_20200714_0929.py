# Generated by Django 3.0.8 on 2020-07-14 06:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0002_track_download_counter'),
    ]

    operations = [
        migrations.AlterField(
            model_name='track',
            name='slug',
            field=models.SlugField(allow_unicode=True, unique=True),
        ),
    ]
