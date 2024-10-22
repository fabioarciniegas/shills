# Generated by Django 2.1.1 on 2018-11-24 19:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('evaluate', '0002_film_scraped_completion'),
    ]

    operations = [
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.AddField(
            model_name='film',
            name='topic_distributions',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='topic',
            name='film',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='evaluate.Film'),
        ),
    ]
