# Generated by Django 5.1.7 on 2025-04-19 04:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0013_rename_vendor_rating_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='UsedItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('category', models.CharField(choices=[('electronics', 'Electronics'), ('clothing', 'Clothing'), ('home', 'Home'), ('books', 'Books'), ('toys', 'Toys'), ('sports', 'Sports'), ('jewelry', 'Jewelry')], default='electronics', max_length=20)),
                ('warranty_period', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='bid',
            name='item',
        ),
        migrations.AddField(
            model_name='bid',
            name='used_item',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='bids', to='api.useditem'),
            preserve_default=False,
        ),
    ]
