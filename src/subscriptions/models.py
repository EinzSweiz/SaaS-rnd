from django.db import models
from django.contrib.auth.models import Group, Permission
from django.conf import settings
from django.db.models.signals import post_save
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

    class Meta:
        permissions = SUBSCRIPTION_PERMISSIONS


    def __str__(self) -> str:
        return self.name




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