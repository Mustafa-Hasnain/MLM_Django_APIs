# Generated by Django 5.0.7 on 2024-08-25 12:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_referral_isactive_referral_updated_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderdetail',
            name='address_line_1',
            field=models.CharField(default=1, max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='orderdetail',
            name='address_line_2',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='orderdetail',
            name='city',
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='orderdetail',
            name='country',
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='orderdetail',
            name='payment_method',
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='orderdetail',
            name='postal_code',
            field=models.CharField(default=1, max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='orderdetail',
            name='shipping_method',
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='orderdetail',
            name='state',
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
    ]
