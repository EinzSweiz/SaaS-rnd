from typing import Iterable
from django.db import models
from django.conf import settings
import helpers.billing
from allauth.account.signals import (
    user_signed_up as allauth_user_signed_up,
    email_confirmed as allauth_email_confirmed,
)

User = settings.AUTH_USER_MODEL
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    strip_id = models.CharField(max_length=120, null=True, blank=True)
    init_email = models.EmailField(blank=True, null=True)
    init_email_confirm = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.user.username}"
    
    def save(self, *args, **kwargs):
        if not self.strip_id:
            if self.init_email and self.init_email_confirm:
                email = self.init_email
                if email != '' or email is not None:
                    stripe_id = helpers.billing.create_customer(email=email, 
                    metadata={'user_id': self.user.id},raw=False),
                    self.strip_id = stripe_id
        super().save(*args, **kwargs)

def allauth_user_signed_up_handler(request, user, *args, **kwargs):
    email = user.email
    Customer.objects.create( 
        user=user,
        init_email=email,
        init_email_confirm=False,
    )

allauth_user_signed_up.connect(allauth_user_signed_up_handler)


def allauth_email_confirmed_handler(request, email_address, *args, **kwargs):
    qs = Customer.objects.filter(
        init_email=email_address,
        init_email_confirm=False
    )
    for obj in qs:
        obj.init_email_confirm=True
        obj.save()

allauth_email_confirmed.connect(allauth_email_confirmed_handler)