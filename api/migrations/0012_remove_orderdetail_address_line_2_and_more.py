# Generated by Django 5.0.7 on 2024-08-26 15:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_orderdetail_address_line_1_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderdetail',
            name='address_line_2',
        ),
        migrations.RemoveField(
            model_name='orderdetail',
            name='payment_method',
        ),
        migrations.RemoveField(
            model_name='orderdetail',
            name='shipping_method',
        ),
    ]
