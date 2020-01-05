from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Patient(models.Model):
    user =models.OneToOneField(User,default=1, on_delete=models.CASCADE )
    identificationCard=models.IntegerField(blank=False,default=0, null=False)
    name=models.CharField(max_length=25,default='blank',blank=False, null=False)
    lastName=models.CharField(max_length=25,default='blank',blank=False, null=False)
    weight=models.IntegerField(blank=False,default=0, null=False)
    height=models.DecimalField(decimal_places=2,max_digits=3,blank=False, null=False)
    size_patient=models.DecimalField(decimal_places=2,max_digits=4,blank=False, null=False)



#class Doctor(models.Model):