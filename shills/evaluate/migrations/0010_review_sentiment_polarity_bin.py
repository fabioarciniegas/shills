# Generated by Django 2.1.1 on 2018-12-11 22:26

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evaluate', '0009_film_polarities_binned'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='sentiment_polarity_bin',
            field=models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(10.0)]),
        ),
    ]
