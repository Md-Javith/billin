# Generated by Django 5.1.6 on 2025-04-23 06:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchase', '0008_alter_purchasepayment_payment_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchasepayment',
            name='payment_type',
            field=models.CharField(choices=[('Cash', 'Cash'), ('Bank', 'Bank'), ('Mixed', 'mixed')], max_length=20),
        ),
    ]
