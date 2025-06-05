from django.db import models

class Medicion(models.Model):
    idMedicion = models.AutoField(primary_key=True)
    fecha = models.DateField(null=True, blank=True)
    PH = models.FloatField(null=True, blank=True)
    MateriaOrganica = models.FloatField(null=True, blank=True)
    Fosforo = models.FloatField(null=True, blank=True)
    Azufre = models.FloatField(null=True, blank=True)
    Calcio = models.FloatField(null=True, blank=True)
    Magnesio = models.FloatField(null=True, blank=True)
    Potasio = models.FloatField(null=True, blank=True)
    Sodio = models.FloatField(null=True, blank=True)
    Hierro = models.FloatField(null=True, blank=True)
    Cobre = models.FloatField(null=True, blank=True)
    Manganeso = models.FloatField(null=True, blank=True)
    Zinc = models.FloatField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'medicion'  


class postMediciones(models.Model):
    idMedicion = models.AutoField(primary_key=True)
    fecha = models.DateField(null=True, blank=True)
    PH = models.FloatField(null=True, blank=True)
    MateriaOrganica = models.FloatField(null=True, blank=True)
    Fosforo = models.FloatField(null=True, blank=True)
    Azufre = models.FloatField(null=True, blank=True)
    Calcio = models.FloatField(null=True, blank=True)
    Magnesio = models.FloatField(null=True, blank=True)
    Potasio = models.FloatField(null=True, blank=True)
    Sodio = models.FloatField(null=True, blank=True)
    Hierro = models.FloatField(null=True, blank=True)
    Cobre = models.FloatField(null=True, blank=True)
    Manganeso = models.FloatField(null=True, blank=True)
    Zinc = models.FloatField(null=True, blank=True)

    class Meta:
        managed = False  
        db_table = 'medicion'
    
    def __str__(self):
        return f'{self.nitrogeno} {self.fosforo} {self.potasio} {self.ph} {self.humedad}'
