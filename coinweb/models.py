from django.db import models
from django.contrib.auth.models import User

PAYMENT_STATUSES = [
    ('auth', 'Waiting for authorisation'),
    ('failed', 'Failed'),
    ('completed', 'Completed')
]

class Account(models.Model):
    django_user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.IntegerField(default=0)  # account balance in cents

class Payment(models.Model):
    nonce = models.TextField(null=True)
    status = models.TextField(choices=PAYMENT_STATUSES)
    from_account = models.ForeignKey(Account, null=True, on_delete=models.SET_NULL)
    # Normally we'd have to_account (and time of initiation, completion, etc),
    # but for this demo we don't need it.
    amount_cents = models.IntegerField()
