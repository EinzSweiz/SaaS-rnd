from django.db import models
from django.contrib.auth.models import Group, Permission
from django.conf import settings
from django.db.models.signals import post_save
import helpers.billing

User = settings.AUTH_USER_MODEL
ALLOW_CUSTOM_GROUPS = True

SUBSCRIPTION_PERMISSIONS = [
            ('advanced', 'Advanced Perm'),
            ('pro', 'Pro Perm'),
            ('basic', 'Basic Perm'),
            ('basic_ai', 'Basic AI Perm'),
        ]

class Subscriptions(models.Model):
    name = models.CharField(max_length=120)
    groups = models.ManyToManyField(Group)
    active = models.BooleanField(default=True)
    permissions = models.ManyToManyField(Permission, 
    limit_choices_to={
        'content_type__app_label': 'subscriptions', 
        'codename__in': [i[0] for i in SUBSCRIPTION_PERMISSIONS]})
    strip_id = models.CharField(max_length=120, null=True, blank=True)


    class Meta:
        permissions = SUBSCRIPTION_PERMISSIONS


    def __str__(self) -> str:
        return self.name
    

class SubscriptionPrice(models.Model):
    class IntervalChoises(models.TextChoices):
        MONTHLY = 'month', 'Monthly'
        YEARLY = 'year', 'Yearly'
    subscription = models.ForeignKey(Subscriptions, on_delete=models.CASCADE, blank=True)
    stripe_id = models.CharField(max_length=120, null=True, blank=True)
    interval = models.CharField(max_length=120,
                                default=IntervalChoises.MONTHLY,
                                choices=IntervalChoises.choices
                            )
    prices = models.DecimalField(max_digits=10, default=99.99, decimal_places=2)

    @property   
    def product_stripe_id(self):
        if not self.subscription:
            return None
        return self.subscription.strip_id
    
    @property
    def stripe_price(self):
        return self.prices * 100
    
    @property
    def stripe_currency(self):
        return 'usd'
    
    def save(self, *args, **kwargs):
        import stripe
        stripe.api_key = "sk_test_4eC39HqLyjWDarjtT1zdp7dc"

        strip_id = helpers.billing.create_price(
        currency=self.stripe_currency,
        unit_amount=self.stripe_price,
        interval=self.interval,
        product=self.product_stripe_id
        )
        
        super.save(*args, **kwargs)

    def save(self, *args, **kwargs):
        if not self.strip_id:
            stripe_id = helpers.billing.create_product( 
            name=self.name,
            metadata={'subscription_plan_id': self.id},
            raw=False),
            self.strip_id = stripe_id
                
        super().save(*args, **kwargs)




class UserSubscriptions(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subscriptions = models.ForeignKey(Subscriptions, 
    on_delete=models.SET_NULL, null=True, blank=True)
    active = models.BooleanField(default=True)



def user_sub_post_save(sender, instance, *args, **kwargs):
    user_sub_instance = instance
    user = user_sub_instance.user
    user_subs = user_sub_instance.subscriptions
    groups_ids = []
    if user_subs is not None:
        groups = user_subs.groups.all()
        groups_ids = groups.values_list('id', flat=True)
    if not ALLOW_CUSTOM_GROUPS:
        user.groups.set(groups_ids)
    else:
        subs_sq = Subscriptions.objects.filter(active=True)
        if user_subs is not None:
            subs_sq = subs_sq.exclude(id=user_subs.id)
        subs_groups = subs_sq.values_list('groups__id', flat=True)
        subs_groups_set = set(subs_groups)
        current_groups = user.groups.all().values_list('id', flat=True)
        groups_ids_set = set(groups_ids)
        current_groups_set = set(current_groups) - subs_groups_set
        final_groups = list(groups_ids_set | current_groups_set)
        user.groups.set(final_groups)

post_save.connect(user_sub_post_save, UserSubscriptions)