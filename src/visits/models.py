from django.db import models

#Create models here 
class PageVisit(models.Model):
    #db -> table 
    path = models.TextField(null=True, blank=True) #col
    timestamp = models.DateTimeField(auto_now_add=True) #col

