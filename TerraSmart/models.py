from django.db import models

class Medicion(models.Model):
    idMedicion = models.AutoField(primary_key=True)
    fecha = models.DateField(null=True, blank=True)
    nitrogeno = models.FloatField(null=True, blank=True)
    fosforo = models.FloatField(null=True, blank=True)
    potasio = models.FloatField(null=True, blank=True)
    ph = models.FloatField(null=True, blank=True)
    humedad = models.FloatField(null=True, blank=True)
    class Meta:
        managed = False
        db_table = 'medicion'  


class postMediciones(models.Model):
    idMedicion = models.AutoField(primary_key=True)
    fecha = models.DateField(null=True, blank=True)
    nitrogeno = models.FloatField(null=True, blank=True)
    fosforo = models.FloatField(null=True, blank=True)
    potasio = models.FloatField(null=True, blank=True)
    ph = models.FloatField(null=True, blank=True)
    humedad = models.FloatField(null=True, blank=True)

    class Meta:
        managed = False  
        db_table = 'medicion'
    
    def __str__(self):
        return f'{self.nitrogeno} {self.fosforo} {self.potasio} {self.ph} {self.humedad}'
