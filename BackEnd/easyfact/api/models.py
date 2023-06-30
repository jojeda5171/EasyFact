from django.db import models
# Create your models here.

class Usuario(models.Model):
   id_usuario=models.AutoField(primary_key=True)
   id_empresa_per=models.CharField(max_length=13)
   correo=models.CharField(max_length=50, unique=True, blank=True, null=True)
   nombre=models.CharField(max_length=20)
   apellido=models.CharField(max_length=20)
   contrasena=models.CharField(max_length=255)

   class Meta:
        managed = False
        db_table = 'usuario'

class Empresa(models.Model):
    id_empresa=models.AutoField(primary_key=True)
    licencia_per=models.CharField(max_length=20,null=False, blank=False, unique=True)
    ruc=models.CharField(max_length=13, unique=True)
    razon_social=models.CharField(max_length=100)
    nombre_comercial=models.CharField(max_length=50)
    direccion=models.CharField(max_length=200)
    telefono=models.CharField(max_length=10)
    logo=models.ImageField(upload_to='static/logos/', blank=True, null=True)
    lleva_contabilidad=models.BooleanField(default=False)
    firma_electronica=models.FileField(upload_to='static/firmas/', blank=True, null=True)
    contrasena_firma_electronica=models.CharField(max_length=255)
    desarrollo=models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = 'empresa'

class Licencia(models.Model):
    licencia=models.CharField(primary_key=True, max_length=20)
    fecha_vencimiento=models.DateField(null=False)
    estado=models.BooleanField(null=False)
