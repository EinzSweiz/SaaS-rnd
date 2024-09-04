from typing import Any
from django.core.management.base import BaseCommand
from subscriptions.models import Subscriptions


class Command(BaseCommand):

    def handle(self, *args: Any, **options: Any):
       qs = Subscriptions.objects.filter(active=True)
       for obj in qs:
            sub_perms = obj.permissions.all()
            for group in obj.groups.all():
                group.permissions.set(sub_perms)
                # for per in obj.permissions.all():
                #     group.permissions.add(per)

