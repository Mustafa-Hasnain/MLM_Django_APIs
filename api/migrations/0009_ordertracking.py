# Generated by Django 5.0.7 on 2024-08-18 13:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_payout_transaction'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderTracking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('in_transit', 'In Transit'), ('out_for_delivery', 'Out for Delivery'), ('delivered', 'Delivered'), ('failed', 'Failed Delivery')], default='pending', max_length=20)),
                ('tracking_number', models.CharField(blank=True, max_length=100, null=True)),
                ('shipped_at', models.DateTimeField(blank=True, null=True)),
                ('estimated_delivery', models.DateField(blank=True, null=True)),
                ('delivery_address', models.TextField(blank=True, null=True)),
                ('last_update', models.DateTimeField(auto_now=True)),
                ('order', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='tracking', to='api.order')),
            ],
        ),
    ]
