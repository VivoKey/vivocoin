# Generated by Django 2.1.1 on 2018-09-01 20:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coinweb', '0002_payment'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='nonce',
            field=models.TextField(null=True),
        ),
    ]
