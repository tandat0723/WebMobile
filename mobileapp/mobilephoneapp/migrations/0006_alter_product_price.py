# Generated by Django 4.1.2 on 2023-08-07 18:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mobilephoneapp', '0005_alter_product_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.IntegerField(max_length=13),
        ),
    ]
