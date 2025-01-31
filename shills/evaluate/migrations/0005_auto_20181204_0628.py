# Generated by Django 2.1.1 on 2018-12-04 06:28

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evaluate', '0004_auto_20181124_2014'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='congruency_score',
            field=models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(100.0)]),
        ),
        migrations.AddField(
            model_name='review',
            name='convolution_score',
            field=models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(100.0)]),
        ),
        migrations.AddField(
            model_name='review',
            name='topicality_score',
            field=models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(100.0)]),
        ),
    ]
