# Generated by Django 4.2.1 on 2023-05-22 08:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('userview', '0002_alter_rating_unique_together'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rating',
            name='audience_rating',
        ),
        migrations.RemoveField(
            model_name='rating',
            name='critic_rating',
        ),
    ]
