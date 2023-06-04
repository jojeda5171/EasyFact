from django.db import models

# Create your models here.

class Usuario(models.Model):
   id_usuario=models.AutoField(primary_key=True)
   id_empresa_per=models.IntegerField()
   correo=models.CharField(max_length=50, unique=True, blank=True, null=True)
   nombre=models.CharField(max_length=20)
   apellido=models.CharField(max_length=20)
   contrasena=models.CharField(max_length=255)

   class Meta:
        managed = False
        db_table = 'usuario'
