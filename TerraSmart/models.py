from django.db import models

#class regisDatos(models.Model):
#    nitrogeno = models.CharField(max_length=100, verbose_name='Nitrogeno')
#    fosforo = models.CharField(max_length=100, verbose_name='Fosforo')
#    potasio = models.CharField(max_length=100, verbose_name='Potasio')
#    ph = models.CharField(max_length=100, verbose_name='ph')
#    humedad = models.CharField(max_length=100, verbose_name='Humedad')

class Medicion(models.Model):
    idMedicion = models.AutoField(primary_key=True)
    fecha = models.DateField(null=True, blank=True)
    Nitrogeno = models.FloatField(null=True, blank=True)
    Fosforo = models.FloatField(null=True, blank=True)
    Medicioncol = models.CharField(max_length=255, null=True, blank=True)  # Ajusta según el tipo real
    potasio = models.FloatField(null=True, blank=True)
    ph = models.FloatField(null=True, blank=True)
    humedad = models.FloatField(null=True, blank=True)
    class Meta:
        managed = False  
        db_table = 'medicion'  

class registroSuelo(models.Model):
    nitrogeno = models.IntegerField(verbose_name='Nitrogeno')
    fosforo = models.IntegerField(verbose_name='Fosforo')
    potasio = models.IntegerField(verbose_name='Potasio')
    ph = models.IntegerField(verbose_name='ph')
    humedad = models.IntegerField(verbose_name='Humedad')

    def __str__(self):
        return f'{self.nitrogeno} {self.fosforo} {self.potasio} {self.ph} {self.humedad}'