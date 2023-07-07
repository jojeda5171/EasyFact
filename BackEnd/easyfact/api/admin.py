from django.contrib import admin
from .models import Usuario, Empresa, Licencia, Iva, Producto, Cliente, Forma_pago

# Register your models here.
admin.site.register(Usuario)
admin.site.register(Empresa)
admin.site.register(Licencia)
admin.site.register(Iva)
admin.site.register(Producto)
admin.site.register(Cliente)
admin.site.register(Forma_pago)