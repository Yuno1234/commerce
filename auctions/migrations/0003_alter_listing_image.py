# Generated by Django 4.1.3 on 2022-12-05 00:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0002_remove_listing_currentbid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='image',
            field=models.URLField(max_length=5000),
        ),
    ]
