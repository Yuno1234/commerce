# Generated by Django 4.1.3 on 2022-12-05 04:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0004_alter_listing_seller'),
    ]

    operations = [
        migrations.RenameField(
            model_name='listing',
            old_name='seller',
            new_name='creator',
        ),
    ]
