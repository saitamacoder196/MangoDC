# Generated by Django 5.1.1 on 2024-09-15 07:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MangoItem',
            fields=[
                ('id', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('folder_path', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image_type', models.CharField(choices=[('original', 'Original'), ('prediction', 'Prediction')], max_length=10)),
                ('position', models.CharField(max_length=10)),
                ('image_path', models.CharField(max_length=255)),
                ('mango_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='mango_analysis.mangoitem')),
            ],
        ),
        migrations.CreateModel(
            name='DetectedArea',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.CharField(max_length=50)),
                ('position_x', models.IntegerField()),
                ('position_y', models.IntegerField()),
                ('area_size', models.FloatField()),
                ('disease', models.CharField(max_length=100)),
                ('mango_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='detected_areas', to='mango_analysis.mangoitem')),
            ],
        ),
        migrations.CreateModel(
            name='Conclusion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_disease_area', models.FloatField()),
                ('total_mango_surface_area', models.FloatField()),
                ('disease_area_percentage', models.FloatField()),
                ('conclusion', models.TextField()),
                ('mango_item', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='conclusion', to='mango_analysis.mangoitem')),
            ],
        ),
    ]