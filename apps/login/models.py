from django.db import models

# Create your models here.
class User(models.Model):
    #clave primaria y auto-incremental para el usuario
    id=models.AutoField(primary_key=True)
    #blanck permite que este campo sea obligatorio (false) o no (True)
    #Para no recibir valores nulos es: null= False
    name=models.CharField(max_length=25,blank=False, null=False)
    lastName=models.CharField(max_length=25,blank=False, null=False)
    password=models.CharField(max_length=40,blank=False, null=False)
    identificationCard=models.IntegerField(blank=False, null=False)

class Patient(models.Model):
    weight=models.IntegerField(blank=False, null=False)
    height=models.DecimalField(decimal_places=2,max_digits=3,blank=False, null=False)
    size_patient=models.DecimalField(decimal_places=2,max_digits=4,blank=False, null=False)
    age=models.DateField(blank=False, null=False)
#class Doctor(models.Model):
    