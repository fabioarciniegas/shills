# Generated by Django 2.1.1 on 2018-12-06 19:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evaluate', '0005_auto_20181204_0628'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='topics_distribution',
            field=models.TextField(default='{}'),
        ),
    ]
