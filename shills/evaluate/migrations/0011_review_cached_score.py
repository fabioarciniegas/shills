# Generated by Django 2.1.1 on 2018-12-15 00:10

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evaluate', '0010_review_sentiment_polarity_bin'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='cached_score',
            field=models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(100.0)]),
        ),
    ]
