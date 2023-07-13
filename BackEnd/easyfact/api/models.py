from django.db import models
# Create your models here.


class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    id_empresa_per = models.CharField(max_length=13)
    correo = models.CharField(
        max_length=100, unique=True, blank=True, null=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    contrasena = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'usuario'


class Empresa(models.Model):
    id_empresa = models.AutoField(primary_key=True)
    licencia_per = models.CharField(
        max_length=20, blank=False, unique=True)
    ruc = models.CharField(max_length=13, unique=True)
    tipo_contribuyente = models.CharField(max_length=100)
    razon_social = models.CharField(max_length=100)
    nombre_comercial = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200)
    telefono = models.CharField(max_length=10)
    logo = models.ImageField(upload_to='static/logos/', blank=True, null=True)
    lleva_contabilidad = models.BooleanField(default=False)
    firma_electronica = models.FileField(
        upload_to='static/firmas/', blank=True, null=True)
    contrasena_firma_electronica = models.CharField(max_length=255)
    desarrollo = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = 'empresa'


class Licencia(models.Model):
    licencia = models.CharField(primary_key=True, max_length=20)
    fecha_vencimiento = models.DateField(null=False)
    estado = models.BooleanField(null=False)

    class Meta:
        managed = False
        db_table = 'licencias'


class Iva(models.Model):
    id_iva = models.AutoField(primary_key=True)
    iva_nombre = models.CharField(max_length=50)
    iva = models.DecimalField(max_digits=4, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'iva'


class Detalle_empresa_iva(models.Model):
    id_detalle_empresa_iva = models.AutoField(primary_key=True)
    id_iva_per = models.IntegerField(auto_created=True)
    id_empresa_per = models.IntegerField(auto_created=True)

    class Meta:
        managed = False
        db_table = 'detalle_empresa_iva'


class Producto(models.Model):
    id_producto = models.AutoField(primary_key=True)
    id_iva_per = models.IntegerField(auto_created=True)
    producto = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'producto'


class Detalle_empresa_producto(models.Model):
    id_detalle_empresa_producto = models.AutoField(primary_key=True)
    id_producto_per = models.IntegerField(auto_created=True)
    id_empresa_per = models.IntegerField(auto_created=True)

    class Meta:
        managed = False
        db_table = 'detalle_empresa_producto'


class Cliente (models.Model):
    id_cliente = models.AutoField(primary_key=True)
    numero_identificacion = models.CharField(max_length=13)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    correo = models.CharField(max_length=100, blank=True, null=True)
    direccion = models.CharField(max_length=200)
    telefono = models.CharField(max_length=10)
    tipo_persona = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'cliente'


class Detalle_empresa_cliente(models.Model):
    id_detalle_empresa_cliente = models.AutoField(primary_key=True)
    id_empresa_per = models.IntegerField(auto_created=True)
    id_cliente_per = models.IntegerField(auto_created=True)

    class Meta:
        managed = False
        db_table = 'detalle_empresa_cliente'


class Forma_pago(models.Model):
    id_forma_pago = models.AutoField(primary_key=True)
    forma_pago = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'forma_pago'


class Factura(models.Model):
    id_factura = models.AutoField(primary_key=True)
    id_cliente_per = models.IntegerField(auto_created=True)
    id_usuario_per = models.IntegerField(auto_created=True)
    # id_usuario_per = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    id_forma_pago_per = models.IntegerField(auto_created=True)
    id_documento_per = models.IntegerField(auto_created=True)
    numero_factura = models.IntegerField(auto_created=True)
    clave_acceso = models.CharField(max_length=49)
    fecha = models.DateField()
    subtotal = models.DecimalField(max_digits=15, decimal_places=2)
    total_iva = models.DecimalField(max_digits=15, decimal_places=2)
    total = models.DecimalField(max_digits=15, decimal_places=2)
    estado = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'factura'


class Detalle_factura(models.Model):
    id_detalle_factura = models.AutoField(primary_key=True)
    id_factura_per = models.IntegerField(auto_created=True)
    id_producto_per = models.IntegerField(auto_created=True)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=15, decimal_places=2)
    subtotal_producto = models.DecimalField(max_digits=15, decimal_places=2)
    total_iva = models.DecimalField(max_digits=15, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'detalle_factura'


class Documento(models.Model):
    id_documento = models.AutoField(primary_key=True)
    xml = models.FileField(upload_to='static/email/xml/', blank=True, null=True)
    ride = models.FileField(upload_to='static/email/pdf/', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'documento'