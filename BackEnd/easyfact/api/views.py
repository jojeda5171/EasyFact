from .constants import SUCCESS_MESSAGE, ERROR_MESSAGE, NOT_DATA_MESSAGE
from django.http import JsonResponse, HttpResponse, FileResponse
from django.core.files.storage import default_storage
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import Usuario, Empresa, Iva, Detalle_empresa_iva, Producto, Detalle_empresa_producto, Cliente, Detalle_empresa_cliente, Licencia, Factura, Detalle_factura, Forma_pago, Documento
from django.db import IntegrityError
from django.views import View
from datetime import date, timedelta
from django.utils.timezone import now

from django.db.models import Max
from io import BytesIO
import json
import os
import re
import requests
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import xml.etree.ElementTree as ET
import base64
import hashlib
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.backends import default_backend
from signxml import XMLSigner, XMLVerifier
from signxml.exceptions import InvalidSignature
import xml.etree.ElementTree as ET

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

from suds.client import Client
import subprocess
import math


# Create your views here.


class UsuarioVista(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, correo=None, contrasena=None):
        if correo or contrasena is not None:
            usuarios = list(Usuario.objects.filter(
                correo=correo, contrasena=contrasena).values())
            if len(usuarios) > 0:
                usuario = usuarios[0]
                datos = {'usuario': usuario}
            else:
                datos = NOT_DATA_MESSAGE
        else:
            usuarios = list(Usuario.objects.values())
            if len(usuarios) > 0:
                datos = {'usuarios': usuarios}
            else:
                datos = NOT_DATA_MESSAGE
        return JsonResponse(datos)

    def post(self, request):
        try:
            jsonData = json.loads(request.body)
            id_empresa_per = Empresa.objects.get(
                ruc=jsonData['id_empresa_per']).id_empresa
            Usuario.objects.create(
                id_empresa_per=id_empresa_per,
                correo=jsonData['correo'],
                nombre=jsonData['nombre'],
                apellido=jsonData['apellido'],
                contrasena=jsonData['contrasena'])
            datos = SUCCESS_MESSAGE
        except IntegrityError as e:
            datos = ERROR_MESSAGE
        except Exception as e:
            datos = ERROR_MESSAGE
        return JsonResponse(datos)

    def put(self, request, correo=None, contrasena=None):
        try:
            jsonData = json.loads(request.body)
            if Usuario.objects.filter(correo=correo, contrasena=contrasena).exists():
                usuario = Usuario.objects.get(
                    correo=correo, contrasena=contrasena)
                empresa = Empresa.objects.get(
                    id_empresa=usuario.id_empresa_per)
                id_empresa_per = empresa.id_empresa
                usuario.id_empresa_per = id_empresa_per
                usuario.correo = jsonData['correo']
                usuario.nombre = jsonData['nombre']
                usuario.apellido = jsonData['apellido']
                usuario.contrasena = jsonData['contrasena']
                usuario.save()
                datos = SUCCESS_MESSAGE
            else:
                datos = NOT_DATA_MESSAGE
        except Exception as e:
            datos = ERROR_MESSAGE
        return JsonResponse(datos)

    def delete(self, request, correo=None, contrasena=None):
        try:
            if Usuario.objects.filter(correo=correo, contrasena=contrasena).exists():
                Usuario.objects.filter(
                    correo=correo, contrasena=contrasena).delete()
                datos = SUCCESS_MESSAGE
            else:
                datos = NOT_DATA_MESSAGE
        except Exception as e:
            datos = ERROR_MESSAGE
        return JsonResponse(datos)


class EmpresaVista(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, id_empresa=None):
        if id_empresa is not None:
            empresas = Empresa.objects.filter(id_empresa=id_empresa).values()
            if len(empresas) > 0:
                empresa = empresas[0]
                datos = {'empresa': empresa}
            else:
                datos = NOT_DATA_MESSAGE
        else:
            empresas = list(Empresa.objects.values())
            if len(empresas) > 0:
                datos = {'empresas': empresas}
            else:
                datos = NOT_DATA_MESSAGE
        return JsonResponse(datos)

    def post(self, request):
        try:
            jsonData = request.POST
            imagen = request.FILES.get('logo')
            firma = request.FILES.get('firma_electronica')
            img_path = os.path.join('static', 'logos', imagen.name)
            img_path = default_storage.save(img_path, imagen)
            firma_path = os.path.join('static', 'firmas', firma.name)
            firma_path = default_storage.save(firma_path, firma)
            with open(img_path, 'wb') as f:
                for chunk in imagen.chunks():
                    f.write(chunk)
            with open(firma_path, 'wb') as f:
                for chunk in firma.chunks():
                    f.write(chunk)
            Empresa.objects.create(
                licencia_per=jsonData['licencia_per'],
                ruc=jsonData['ruc'],
                tipo_contribuyente=jsonData['tipo_contribuyente'],
                razon_social=jsonData['razon_social'],
                nombre_comercial=jsonData['nombre_comercial'],
                direccion=jsonData['direccion'],
                telefono=jsonData['telefono'],
                logo=img_path,
                lleva_contabilidad=jsonData['lleva_contabilidad'],
                firma_electronica=firma_path,
                contrasena_firma_electronica=jsonData['contrasena_firma_electronica'],
                desarrollo=jsonData['desarrollo']
            )
            datos = SUCCESS_MESSAGE
        except IntegrityError as e:
            datos = ERROR_MESSAGE
        except Exception as e:
            datos = ERROR_MESSAGE
        return JsonResponse(datos)

    def put(self, request, id_empresa=None):
        try:
            jsonData = json.loads(request.body)
            if Empresa.objects.filter(id_empresa=id_empresa).exists():
                empresa = Empresa.objects.get(id_empresa=id_empresa)
                empresa.ruc = jsonData['ruc']
                empresa.tipo_contribuyente = jsonData['tipo_contribuyente']
                empresa.razon_social = jsonData['razon_social']
                empresa.nombre_comercial = jsonData['nombre_comercial']
                empresa.direccion = jsonData['direccion']
                empresa.telefono = jsonData['telefono']
                empresa.lleva_contabilidad = jsonData['lleva_contabilidad']
                empresa.contrasena_firma_electronica = jsonData['contrasena_firma_electronica']
                empresa.desarrollo = jsonData['desarrollo']
                empresa.save()
                datos = SUCCESS_MESSAGE
            else:
                datos = NOT_DATA_MESSAGE
        except Exception as e:
            datos = ERROR_MESSAGE
        return JsonResponse(datos)

    def delete(self, request, id_empresa=None):
        try:
            if Empresa.objects.filter(id_empresa=id_empresa).exists():
                Empresa.objects.filter(id_empresa=id_empresa).delete()
                datos = SUCCESS_MESSAGE
            else:
                datos = NOT_DATA_MESSAGE
        except Exception as e:
            datos = ERROR_MESSAGE
        return JsonResponse(datos)


class LogoVista(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, id_empresa=None):
        try:
            empresa = Empresa.objects.get(id_empresa=id_empresa)
            imagen_path = empresa.logo.path
            with open(imagen_path, 'rb') as file:
                response = HttpResponse(file.read(), content_type='image/jpeg')
                return response
        except Empresa.DoesNotExist:
            datos = ERROR_MESSAGE
        except Exception as e:
            datos = ERROR_MESSAGE
        return JsonResponse(datos)

    def post(self, request, id_empresa=None):
        try:
            empresa = Empresa.objects.get(id_empresa=id_empresa)
            imagen = request.FILES.get('logo')
            imagen_path = os.path.join('static', 'logos', imagen.name)
            imagen_path = default_storage.save(imagen_path, imagen)
            with open(imagen_path, 'wb') as f:
                for chunk in imagen.chunks():
                    f.write(chunk)
            empresa.logo = imagen_path
            empresa.save()
            datos = SUCCESS_MESSAGE
        except Empresa.DoesNotExist:
            datos = ERROR_MESSAGE
        except Exception as e:
            datos = ERROR_MESSAGE
        return JsonResponse(datos)


class FirmaVista(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, id_empresa=None):
        try:
            empresa = Empresa.objects.get(id_empresa=id_empresa)
            firma_path = empresa.firma_electronica.path
            nombre_archivo = os.path.basename(firma_path)
            response = FileResponse(open(firma_path, 'rb'))
            response['Content-Disposition'] = 'attachment; filename="{}"'.format(
                nombre_archivo)
            return response
        except Empresa.DoesNotExist:
            datos = ERROR_MESSAGE
        except Exception as e:
            datos = ERROR_MESSAGE
        return JsonResponse(datos)

    def post(self, request, id_empresa=None):
        try:
            empresa = Empresa.objects.get(id_empresa=id_empresa)
            firma = request.FILES.get('firma_electronica')
            firma_path = os.path.join('static', 'firmas', firma.name)
            firma_path = default_storage.save(firma_path, firma)
            with open(firma_path, 'wb') as f:
                for chunk in firma.chunks():
                    f.write(chunk)
            empresa.firma_electronica = firma_path
            empresa.save()
            datos = SUCCESS_MESSAGE
        except Empresa.DoesNotExist:
            datos = ERROR_MESSAGE
        except Exception as e:
            datos = ERROR_MESSAGE
        return JsonResponse(datos)


class IvaVista(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, id_empresa=None, iva_nombre=None):
        try:
            if iva_nombre is not None:
                iva = list(Iva.objects.filter(id_iva__in=Detalle_empresa_iva.objects.filter(
                    id_empresa_per=id_empresa).values('id_iva_per'), iva_nombre=iva_nombre).values())
                if len(iva) > 0:
                    datos = {'iva': iva[0]}
                else:
                    datos = NOT_DATA_MESSAGE
            else:
                ivas = list(Iva.objects.filter(id_iva__in=Detalle_empresa_iva.objects.filter(
                    id_empresa_per=id_empresa).values('id_iva_per')).values())
                datos = {'ivas': ivas}
        except Exception as e:
            datos = ERROR_MESSAGE
        except Empresa.DoesNotExist:
            datos = ERROR_MESSAGE
        except Iva.DoesNotExist:
            datos = ERROR_MESSAGE
        except Detalle_empresa_iva.DoesNotExist:
            datos = ERROR_MESSAGE
        except IndexError:
            datos = NOT_DATA_MESSAGE
        return JsonResponse(datos)

    def post(self, request, id_empresa=None):
        try:
            jsonData = json.loads(request.body)
            if (Iva.objects.filter(iva_nombre=jsonData['iva_nombre']).exists()):
                id_iva = Iva.objects.filter(
                    iva_nombre=jsonData['iva_nombre']).values('id_iva').first()['id_iva']
                if (Detalle_empresa_iva.objects.filter(id_iva_per=id_iva, id_empresa_per=id_empresa).exists()):
                    datos = SUCCESS_MESSAGE
                else:
                    Detalle_empresa_iva.objects.create(
                        id_iva_per=id_iva,
                        id_empresa_per=id_empresa
                    )
                    datos = SUCCESS_MESSAGE
            else:
                nuevo_iva = Iva.objects.create(
                    iva_nombre=jsonData['iva_nombre'],
                    iva=jsonData['iva']
                )
                Detalle_empresa_iva.objects.create(
                    id_iva_per=nuevo_iva.id_iva,
                    id_empresa_per=id_empresa
                )
                datos = SUCCESS_MESSAGE
        except Exception as e:
            datos = ERROR_MESSAGE
        return JsonResponse(datos)

    def put(self, request, id_empresa=None, iva_nombre=None):
        try:
            jsonData = json.loads(request.body)
            if Iva.objects.filter(iva_nombre=iva_nombre).exists():
                iva = Iva.objects.filter(iva_nombre=iva_nombre).first()
                iva.iva_nombre = jsonData['iva_nombre']
                iva.iva = jsonData['iva']
                iva.save()
                datos = SUCCESS_MESSAGE
            else:
                datos = NOT_DATA_MESSAGE
        except Exception as e:
            datos = ERROR_MESSAGE
        return JsonResponse(datos)

    def delete(self, request, id_empresa=None, iva_nombre=None):
        try:
            id_iva = Iva.objects.filter(iva_nombre=iva_nombre).values(
                'id_iva').first()['id_iva']
            Detalle_empresa_iva.objects.filter(
                id_empresa_per=id_empresa, id_iva_per=id_iva).delete()
            datos = SUCCESS_MESSAGE
        except Exception as e:
            datos = ERROR_MESSAGE
        return JsonResponse(datos)


class ProductoVista(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, id_empresa=None, producto=None):
        try:
            if producto is not None:
                producto = list(Producto.objects.filter(id_producto__in=Detalle_empresa_producto.objects.filter(
                    id_empresa_per=id_empresa).values('id_producto_per'), producto=producto).values())
                if len(producto) > 0:
                    datos = {'producto': producto[0]}
                else:
                    datos = NOT_DATA_MESSAGE
            else:
                productos = list(Producto.objects.filter(id_producto__in=Detalle_empresa_producto.objects.filter(
                    id_empresa_per=id_empresa).values('id_producto_per')).values())
                datos = {'productos': productos}
        except Exception as e:
            datos = ERROR_MESSAGE
        except Empresa.DoesNotExist:
            datos = ERROR_MESSAGE
        except Producto.DoesNotExist:
            datos = ERROR_MESSAGE
        except Detalle_empresa_producto.DoesNotExist:
            datos = ERROR_MESSAGE
        except IndexError:
            datos = NOT_DATA_MESSAGE
        return JsonResponse(datos)

    def post(self, request, id_empresa=None):
        try:
            jsonData = json.loads(request.body)
            nuevo_producto = Producto.objects.create(
                id_iva_per=jsonData['id_iva_per'],
                producto=jsonData['producto'],
                precio=jsonData['precio']
            )
            Detalle_empresa_producto.objects.create(
                id_producto_per=nuevo_producto.id_producto,
                id_empresa_per=id_empresa
            )
            datos = SUCCESS_MESSAGE
        except Exception as e:
            datos = ERROR_MESSAGE
        return JsonResponse(datos)

    def put(self, request, id_empresa=None, id_producto=None):
        try:
            jsonData = json.loads(request.body)
            if Producto.objects.filter(id_producto=id_producto).exists():
                producto = Producto.objects.filter(id_producto__in=Detalle_empresa_producto.objects.filter(
                    id_empresa_per=id_empresa).values('id_producto_per'), id_producto=id_producto).update(producto=jsonData['producto'], precio=jsonData['precio'])
                datos = SUCCESS_MESSAGE
            else:
                datos = NOT_DATA_MESSAGE
        except Exception as e:
            datos = ERROR_MESSAGE
        except Producto.DoesNotExist:
            datos = ERROR_MESSAGE
        except Detalle_empresa_producto.DoesNotExist:
            datos = ERROR_MESSAGE
        except Empresa.DoesNotExist:
            datos = ERROR_MESSAGE
        return JsonResponse(datos)

    def delete(self, request, id_empresa=None, id_producto=None):
        try:
            producto = Detalle_empresa_producto.objects.filter(
                id_empresa_per=id_empresa, id_producto_per=id_producto).delete()
            datos = SUCCESS_MESSAGE
        except Exception as e:
            datos = ERROR_MESSAGE
        except Producto.DoesNotExist:
            datos = ERROR_MESSAGE
        except Detalle_empresa_producto.DoesNotExist:
            datos = ERROR_MESSAGE
        except Empresa.DoesNotExist:
            datos = ERROR_MESSAGE
        return JsonResponse(datos)


class IconoProductoVista(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, ruc, producto):
        try:
            empresa = Empresa.objects.get(ruc=ruc).id_empresa
            producto = Producto.objects.filter(id_producto__in=Detalle_empresa_producto.objects.filter(
                id_empresa_per=empresa).values('id_producto_per'), producto=producto).values().first()
            if producto is not None:
                icono_path = producto['icono']
                with open(icono_path, 'rb') as f:
                    return HttpResponse(f.read(), content_type='image/jpeg')
            else:
                return HttpResponse(status=404)
        except Empresa.DoesNotExist:
            return HttpResponse(status=404)

    def post(self, request, ruc, producto):
        try:
            empresa = Empresa.objects.get(ruc=ruc).id_empresa
            producto = Producto.objects.filter(id_producto__in=Detalle_empresa_producto.objects.filter(
                id_empresa_per=empresa).values('id_producto_per'), producto=producto).first()
            if producto is not None:
                icono = request.FILES.get('icono')
                img_path = os.path.join('static', 'iconos', icono.name)
                img_path = default_storage.save(img_path, icono)
                producto.icono = img_path
                producto.save(update_fields=['icono'])
                datos = SUCCESS_MESSAGE
            else:
                datos = NOT_DATA_MESSAGE
        except Exception as e:
            datos = ERROR_MESSAGE
        return JsonResponse(datos)


class IvaProductoVista(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def put(self, request, ruc, producto):
        try:
            jsonData = json.loads(request.body)
            empresa = Empresa.objects.get(ruc=ruc).id_empresa
            print(Producto.objects.filter(producto=producto).exists())
            if Producto.objects.filter(producto=producto).exists():
                producto = Producto.objects.filter(id_producto__in=Detalle_empresa_producto.objects.filter(
                    id_empresa_per=empresa).values('id_producto_per'), producto=producto).update(id_iva_per=Iva.objects.filter(iva_nombre=jsonData['id_iva_per']).values('id_iva').first()['id_iva'])
                datos = SUCCESS_MESSAGE
            else:
                datos = NOT_DATA_MESSAGE
        except Exception as e:
            datos = ERROR_MESSAGE
        return JsonResponse(datos)


class ClienteVista(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    # def get(self, request, numero_identificacion=None, ruc=None):
    def get(self, request, id_cliente=None, id_empresa=None):
        try:
            if id_cliente is not None and Cliente.objects.filter(id_cliente__in=Detalle_empresa_cliente.objects.filter(id_empresa_per=id_empresa).values('id_cliente_per'), id_cliente=id_cliente).exists():
                cliente = Cliente.objects.filter(id_cliente__in=Detalle_empresa_cliente.objects.filter(
                    id_empresa_per=id_empresa).values('id_cliente_per'), id_cliente=id_cliente).values().first()
                datos = {'cliente': cliente}
            elif id_cliente is None and id_empresa is not None:
                clientes = list(Cliente.objects.filter(id_cliente__in=Detalle_empresa_cliente.objects.filter(
                    id_empresa_per=id_empresa).values('id_cliente_per')).values())
                datos = {'clientes': clientes}
            else:
                datos = NOT_DATA_MESSAGE
        except Exception as e:
            datos = ERROR_MESSAGE
        except Cliente.DoesNotExist:
            datos = NOT_DATA_MESSAGE
        except IndexError:
            datos = NOT_DATA_MESSAGE
        return JsonResponse(datos)

    def post(self, request, id_empresa=None):
        try:
            jsonData = json.loads(request.body)
            if (Cliente.objects.filter(numero_identificacion=jsonData['numero_identificacion']).exists()):
                id_cliente = Cliente.objects.filter(
                    numero_identificacion=jsonData['numero_identificacion']).values('id_cliente').first()['id_cliente']
                if (Detalle_empresa_cliente.objects.filter(id_empresa_per=id_empresa, id_cliente_per=id_cliente).exists()):
                    datos = SUCCESS_MESSAGE
                else:
                    Detalle_empresa_cliente.objects.create(
                        id_empresa_per=id_empresa,
                        id_cliente_per=id_cliente
                    )
                    datos = SUCCESS_MESSAGE
            else:
                cliente = Cliente.objects.create(
                    numero_identificacion=jsonData['numero_identificacion'],
                    nombre=jsonData['nombre'],
                    apellido=jsonData['apellido'],
                    direccion=jsonData['direccion'],
                    telefono=jsonData['telefono'],
                    correo=jsonData['correo'],
                    tipo_persona=jsonData['tipo_persona']
                )
                Detalle_empresa_cliente.objects.create(
                    id_empresa_per=id_empresa,
                    id_cliente_per=cliente.id_cliente
                )
                datos = SUCCESS_MESSAGE
        except Exception as e:
            datos = ERROR_MESSAGE
        except Empresa.DoesNotExist:
            datos = ERROR_MESSAGE
        return JsonResponse(datos)

    def put(self, request, numero_identificacion=None, id_empresa=None):
        try:
            jsonData = json.loads(request.body)
            if Cliente.objects.filter(id_cliente__in=Detalle_empresa_cliente.objects.filter(id_empresa_per=id_empresa).values('id_cliente_per'), numero_identificacion=numero_identificacion).exists():
                Cliente.objects.filter(id_cliente__in=Detalle_empresa_cliente.objects.filter(id_empresa_per=id_empresa).values('id_cliente_per'), numero_identificacion=numero_identificacion).update(
                    nombre=jsonData['nombre'],
                    apellido=jsonData['apellido'],
                    direccion=jsonData['direccion'],
                    telefono=jsonData['telefono'],
                    correo=jsonData['correo'],
                    tipo_persona=jsonData['tipo_persona']
                )
                datos = SUCCESS_MESSAGE
            else:
                datos = NOT_DATA_MESSAGE
        except Exception as e:
            datos = ERROR_MESSAGE
        except Cliente.DoesNotExist:
            datos = NOT_DATA_MESSAGE
        return JsonResponse(datos)

    def delete(self, request, numero_identificacion=None, id_empresa=None):
        try:
            id_cliente = Cliente.objects.get(
                numero_identificacion=numero_identificacion).id_cliente
            if Detalle_empresa_cliente.objects.filter(id_empresa_per=id_empresa, id_cliente_per=id_cliente).exists():
                Detalle_empresa_cliente.objects.filter(
                    id_empresa_per=id_empresa, id_cliente_per=id_cliente).delete()
                datos = SUCCESS_MESSAGE
            else:
                datos = NOT_DATA_MESSAGE
        except Exception as e:
            datos = ERROR_MESSAGE
        return JsonResponse(datos)


class LicenciaVista(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def put(self, request, ruc=None):
        try:
            jsonData = json.loads(request.body)
            if Licencia.objects.filter(licencia=jsonData['licencia']).exists():
                if Licencia.objects.filter(licencia=jsonData['licencia']).values('estado').first()['estado']:
                    Empresa.objects.filter(ruc=ruc).update(
                        licencia_per=jsonData['licencia'])
                    datos = SUCCESS_MESSAGE
                else:
                    datos = ERROR_MESSAGE
            else:
                datos = ERROR_MESSAGE
        except Exception as e:
            datos = ERROR_MESSAGE
        return JsonResponse(datos)


class AbrirFacturaView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        try:
            jsonData = json.loads(request.body)
            cliente_id = Cliente.objects.get(
                numero_identificacion='9999999999999').id_cliente
            usuario = Usuario.objects.get(
                id_usuario=jsonData['id_usuario_per'])
            numero_factura = self.numero_factura(usuario.id_empresa_per)
            factura = Factura.objects.create(
                id_cliente_per=cliente_id,
                id_usuario_per=usuario.id_usuario,
                numero_factura=numero_factura,
                fecha=datetime.now().date(),
                estado='abierta'
            )
            factura = list(Factura.objects.filter(
                id_factura=factura.id_factura).values())

            datos = {'factura': factura}
            # datos = factura
        except Exception as e:
            datos = ERROR_MESSAGE
        return JsonResponse(datos)

    def numero_factura(self, id_empresa_per):
        facturas_empresa = Factura.objects.filter(id_usuario_per__in=Usuario.objects.filter(
            id_empresa_per=id_empresa_per).values('id_usuario'))
        numero_factura = facturas_empresa.aggregate(Max('numero_factura'))[
            'numero_factura__max']
        if numero_factura is None:
            numero_factura = 1
        else:
            numero_factura = numero_factura+1
        return numero_factura

    def put(self, request, id_factura=None):
        try:
            jsonData = json.loads(request.body)
            if Factura.objects.filter(id_factura=id_factura).exists():
                Factura.objects.filter(id_factura=id_factura).update(
                    id_cliente_per=Cliente.objects.get(numero_identificacion=jsonData['id_cliente_per']).id_cliente)
                datos = SUCCESS_MESSAGE
            else:
                datos = NOT_DATA_MESSAGE
        except Exception as e:
            datos = ERROR_MESSAGE
        return JsonResponse(datos)

    def delete(self, request, id_factura=None):
        try:
            if Factura.objects.filter(id_factura=id_factura).exists():
                Factura.objects.filter(id_factura=id_factura, estado="abierta").delete()
                datos = SUCCESS_MESSAGE
            else:
                datos = NOT_DATA_MESSAGE
        except Exception as e:
            datos = ERROR_MESSAGE
        return JsonResponse(datos)


class AgregarProductoView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        try:
            jsonData = json.loads(request.body)
            #id_factura_per, id_producto_per, cantidad
            #usuario = Usuario.objects.get(id_usuario=jsonData['id_usuario_per'])
            #factura = Factura.objects.get(
                #numero_factura=jsonData['id_factura_per'], estado='abierta', id_cliente_per=Cliente.objects.get(numero_identificacion=jsonData['id_cliente_per']).id_cliente, id_usuario_per=usuario.id_usuario)
            factura = Factura.objects.get(id_factura=jsonData['id_factura_per'])
            if Factura.objects.filter(id_factura=factura.id_factura).exists() and Producto.objects.filter(id_producto=jsonData['id_producto_per']).exists():
                producto = Producto.objects.filter(
                    id_producto=jsonData['id_producto_per']).values().first()
                iva = Iva.objects.get(id_iva=producto['id_iva_per'])
                detalle_factura = Detalle_factura.objects.create(
                    id_factura_per=factura.id_factura,
                    id_producto_per=producto['id_producto'],
                    cantidad=jsonData['cantidad'],
                    precio_unitario=producto['precio'],
                    subtotal_producto=float(
                        jsonData['cantidad']) * float(producto['precio']),
                    total_iva=float(jsonData['cantidad']) *
                    float(producto['precio']) * float(iva.iva)
                )
                datos = SUCCESS_MESSAGE
            else:
                datos = ERROR_MESSAGE
        except Exception as e:
            datos = ERROR_MESSAGE
        return JsonResponse(datos)

    def get(self, request, id_factura=None):
        try:
            detalle_factura = Detalle_factura.objects.filter(
                id_factura_per=id_factura).values()
            datos = {"Detalles": list(detalle_factura)}
        except Exception as e:
            datos = ERROR_MESSAGE
        return JsonResponse(datos)


class MostrarFacturaView(View):
    def get(self, request, id_empresa=None):
        try:
            facturas_empresa= Factura.objects.filter(id_usuario_per__in=Usuario.objects.filter( 
                id_empresa_per=id_empresa).values('id_usuario'), estado='cerrada').values()
            if facturas_empresa.exists():
                #cambiar el id del cliente por el nombre del cliente
                for factura in facturas_empresa:
                    factura['id_cliente_per'] = Cliente.objects.get(id_cliente=factura['id_cliente_per']).nombre
                datos = {"Facturas": list(facturas_empresa)}
            else:
                datos = {"Facturas": []}
        except Exception as e:
            datos = ERROR_MESSAGE
        return JsonResponse(datos)


class CerrarFacturaView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        factura = Factura.objects.get(id_factura=jsonData['id_factura_per'])
        try:
            jsonData = json.loads(request.body)
            usuario = Usuario.objects.get(id_usuario=factura.id_usuario_per)
            empresa = Empresa.objects.get(id_empresa=usuario.id_empresa_per)
            if factura is not None:
                factura.id_forma_pago_per = jsonData['id_forma_pago_per']
                factura.clave_acceso = self.generar_clave_acceso(factura.fecha.strftime(
                    '%d%m%Y'), '01', empresa.ruc, '1', '001100', str(factura.numero_factura).zfill(9), '71011173', '1')
                subtotal = 0
                total_iva = 0
                total = 0
                for detalle in Detalle_factura.objects.filter(id_factura_per=factura.id_factura):
                    subtotal += detalle.subtotal_producto
                    total_iva += detalle.total_iva
                    total += detalle.subtotal_producto + detalle.total_iva
                factura.subtotal = subtotal
                factura.total_iva = total_iva
                factura.total = total
                factura.id_cliente_per = jsonData['id_cliente_per']
                factura.estado = 'cerrada'
                factura.save()
                ride = self.generar_pdf_factura(factura, Detalle_factura.objects.filter(
                    id_factura_per=factura.id_factura, id_producto_per__in=Detalle_empresa_producto.objects.filter(id_empresa_per=usuario.id_empresa_per).values('id_producto_per')))
                xml_data = self.generar_xml(factura, Detalle_factura.objects.filter(
                    id_factura_per=factura.id_factura, id_producto_per__in=Detalle_empresa_producto.objects.filter(id_empresa_per=usuario.id_empresa_per).values('id_producto_per')), empresa)
                signed_xml = self.firmar_xml(xml_data, factura)
                validar = self.validar_xml(signed_xml)
                documentos = self.guardar_comprobantes(
                    ride, signed_xml, factura.clave_acceso)
                self.enviar_comprobante_correo(documentos, factura)
                datos = {"Factura": factura}
            else:
                datos = ERROR_MESSAGE
        except:
            factura.estado = 'abierta'
            factura.save()
            datos = ERROR_MESSAGE
        return JsonResponse(datos)

    def generar_pdf_factura(self, factura, detalles_factura):
        empresa = Empresa.objects.get(id_empresa=Usuario.objects.filter(
            id_usuario=factura.id_usuario_per).values('id_empresa_per').first()['id_empresa_per'])
        cliente = Cliente.objects.get(id_cliente=factura.id_cliente_per)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="factura_{factura.numero_factura}.pdf"'

        # Crear el objeto canvas y establecer el tamaño de página
        page_width, page_height = letter
        left_margin = 20  # Margen izquierdo en puntos
        right_margin = 20  # Margen derecho en puntos
        p = SimpleDocTemplate(response, pagesize=(
            page_width, page_height), leftMargin=left_margin, rightMargin=right_margin)

        # Estilos de texto
        styles = getSampleStyleSheet()
        style_title = styles["Title"]
        style_body = styles["BodyText"]

        # Contenido del PDF
        elements = []

        # Agregar la tabla con dos columnas
        table_data = [
            [
                [
                    Image(empresa.logo.path, width=275,
                          height=100),  # Logo de la empresa
                    # Razón Social de la empresa
                    Paragraph(
                        f'Razón Social: {empresa.razon_social}', style_body),
                    # Dirección de la empresa
                    Paragraph(f'Dirección: {empresa.direccion}', style_body),
                    # Obligado a llevar contabilidad
                    Paragraph(
                        f'Obligado a llevar contabilidad: {"SI" if empresa.lleva_contabilidad else "NO"}', style_body),
                ],
                [
                    # RUC de la empresa
                    Paragraph(f'RUC: {empresa.ruc}', style_body),
                    # Número de factura
                    Paragraph(
                        f'Número de factura: {factura.numero_factura}', style_body),
                    # Fecha de la factura
                    Paragraph(f'Fecha: {factura.fecha}', style_body),
                    # Ambiente
                    Paragraph(
                        f'Ambiente: {"Desarrollo" if empresa.desarrollo else "Producción"}', style_body),
                    Paragraph(
                        f'Clave de acceso: {factura.clave_acceso}', style_body),
                ]
            ]
        ]
        table = Table(table_data, colWidths=[
                      275, 275], hAlign='CENTER', vAlign='MIDDLE')
        style_table = TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),  # Margen izquierdo
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),  # Margen derecho
        ])
        table.setStyle(style_table)
        elements.append(table)
        elements.append(Spacer(2, 20))
        data_cliente = [
            [
                [
                    Paragraph('Cliente:', style_body),
                    Paragraph('RUC:', style_body),
                    Paragraph('Dirección:', style_body),
                    Paragraph('Teléfono:', style_body),
                    Paragraph('Correo electrónico:', style_body),
                ],
                [
                    Paragraph(cliente.nombre+' ' +
                              cliente.apellido, style_body),
                    Paragraph(cliente.numero_identificacion, style_body),
                    Paragraph(cliente.direccion, style_body),
                    Paragraph(cliente.telefono, style_body),
                    Paragraph(cliente.correo, style_body),
                ]
            ]
        ]

        table_cliente = Table(data_cliente, colWidths=[
                              110, 440], hAlign='CENTER', vAlign='MIDDLE')
        table_cliente.setStyle(style_table)

        elements.append(table_cliente)
        elements.append(Spacer(2, 20))
        # Agregar la tabla de detalles de factura
        table_data = [['Cantidad', 'Producto', 'V. Unitario', 'V. Total']]
        for detalle in detalles_factura:
            table_data.append([
                str(detalle.cantidad),
                str(Producto.objects.filter(id_producto__in=Detalle_empresa_producto.objects.filter(
                    id_empresa_per=empresa.id_empresa).values('id_producto_per'), id_producto=detalle.id_producto_per).values().first()['producto']),
                str(detalle.precio_unitario),
                str(detalle.subtotal_producto)
            ])

        table = Table(table_data, colWidths=[
                      60, 290, 90, 120], hAlign='CENTER', vAlign='MIDDLE')
        style_table = TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),  # Margen izquierdo
            ('RIGHTPADDING', (0, 0), (0, 0), 5),  # Margen derecho
        ])
        table.setStyle(style_table)
        elements.append(table)
        data_iva_total = [
            [
                [
                    Paragraph('Subtotal:', style_body),
                    Paragraph('IVA:', style_body),
                    Paragraph('Total:', style_body),
                ],
                [
                    Paragraph(str(round(factura.subtotal, 3)), style_body),
                    Paragraph(str(round(factura.total_iva, 3)), style_body),
                    Paragraph(str(round(factura.total, 3)), style_body),
                ]
            ]
        ]
        table_iva_total = Table(data_iva_total, colWidths=[
                                90, 120], hAlign='RIGHT', vAlign='MIIDDLE')
        style_table_iva_total = TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),  # Margen izquierdo
            ('RIGHTPADDING', (0, 0), (0, 0), 5),  # Margen derecho

        ])
        table_iva_total.setStyle(style_table_iva_total)
        elements.append(table_iva_total)

        # Generar el PDF con los elementos
        p.build(elements)
        pdf_bytes = response.getvalue()
        pdf_file_path = os.path.join(
            'static', 'email', 'pdf', f'factura_{factura.clave_acceso}.pdf')
        with open(pdf_file_path, 'wb') as pdf_file:
            pdf_file.write(pdf_bytes)
        return pdf_file_path

    def generar_xml(self, factura_recibida, detalles_factura, empresa):
        cliente = Cliente.objects.filter(
            id_cliente=factura_recibida.id_cliente_per).values().first()
        factura = ET.Element('factura')
        factura.set('id', 'comprobante')
        factura.set('version', '1.1.0')

        info_tributaria = ET.SubElement(factura, 'infoTributaria')
        ambiente = ET.SubElement(info_tributaria, 'ambiente')
        ambiente.text = '1'
        tipo_emision = ET.SubElement(info_tributaria, 'tipoEmision')
        tipo_emision.text = '1'
        razon_social = ET.SubElement(info_tributaria, 'razonSocial')
        razon_social.text = empresa.razon_social
        ruc = ET.SubElement(info_tributaria, 'ruc')
        ruc.text = empresa.ruc
        fecha_actual = date.today().strftime('%d%m%Y')
        clave_acceso = ET.SubElement(info_tributaria, 'claveAcceso')
        clave_acceso.text = factura_recibida.clave_acceso
        cod_doc = ET.SubElement(info_tributaria, 'codDoc')
        cod_doc.text = '01'
        estab = ET.SubElement(info_tributaria, 'estab')
        estab.text = '001'
        pto_emi = ET.SubElement(info_tributaria, 'ptoEmi')
        pto_emi.text = '100'
        secuencial = ET.SubElement(info_tributaria, 'secuencial')
        secuencial.text = str(factura_recibida.numero_factura).zfill(9)
        dir_matriz = ET.SubElement(info_tributaria, 'dirMatriz')
        dir_matriz.text = empresa.direccion

        info_factura = ET.SubElement(factura, 'infoFactura')
        fecha_emision = ET.SubElement(info_factura, 'fechaEmision')
        fecha_emision.text = factura_recibida.fecha.strftime('%d/%m/%Y')
        dir_establecimiento = ET.SubElement(info_factura, 'dirEstablecimiento')
        dir_establecimiento.text = empresa.direccion
        obligado_contabilidad = ET.SubElement(
            info_factura, 'obligadoContabilidad')
        obligado_contabilidad.text = 'SI' if (
            empresa.lleva_contabilidad) else 'NO'
        tipo_identificacion_comprador = ET.SubElement(
            info_factura, 'tipoIdentificacionComprador')
        tipo_identificacion_comprador.text = '04'
        razon_social_comprador = ET.SubElement(
            info_factura, 'razonSocialComprador')
        razon_social_comprador.text = cliente['nombre'] + \
            ' ' + cliente['apellido']
        identificacion_comprador = ET.SubElement(
            info_factura, 'identificacionComprador')
        identificacion_comprador.text = '07' if cliente['numero_identificacion'] == '9999999999999' else ('04' if len(
            cliente['numero_identificacion']) == 13 and cliente['numero_identificacion'][-3:] == '001' else '05')
        total_sin_impuestos = ET.SubElement(info_factura, 'totalSinImpuestos')
        total_sin_impuestos.text = str(factura_recibida.subtotal)
        total_descuento = ET.SubElement(info_factura, 'totalDescuento')
        total_descuento.text = '0.00'

        total_con_impuestos = ET.SubElement(info_factura, 'totalConImpuestos')
        total_impuesto = ET.SubElement(total_con_impuestos, 'totalImpuesto')
        codigo = ET.SubElement(total_impuesto, 'codigo')
        codigo.text = '2'
        codigo_porcentaje = ET.SubElement(total_impuesto, 'codigoPorcentaje')
        codigo_porcentaje.text = '0' if factura_recibida.total_iva == 0.00 else '2'
        base_imponible = ET.SubElement(total_impuesto, 'baseImponible')
        base_imponible.text = str(factura_recibida.subtotal)
        valor = ET.SubElement(total_impuesto, 'valor')
        valor.text = str(factura_recibida.total_iva)

        propina = ET.SubElement(info_factura, 'propina')
        propina.text = '0'
        importe_total = ET.SubElement(info_factura, 'importeTotal')
        importe_total.text = str(factura_recibida.total)
        moneda = ET.SubElement(info_factura, 'moneda')
        moneda.text = 'DOLAR'

        pagos = ET.SubElement(info_factura, 'pagos')
        pago = ET.SubElement(pagos, 'pago')
        forma_pago = ET.SubElement(pago, 'formaPago')
        forma_pago.text = '01'
        total_pago = ET.SubElement(pago, 'total')
        total_pago.text = str(factura_recibida.total)

        detalles = ET.SubElement(factura, 'detalles')

        for detalle in detalles_factura:
            detalle_element = ET.SubElement(detalles, 'detalle')
            codigo_principal = ET.SubElement(
                detalle_element, 'codigoPrincipal')
            codigo_principal.text = str(detalle.id_producto_per)
            descripcion = ET.SubElement(detalle_element, 'descripcion')
            descripcion.text = Producto.objects.get(
                id_producto=detalle.id_producto_per).producto
            cantidad = ET.SubElement(detalle_element, 'cantidad')
            cantidad.text = str(detalle.cantidad)
            precio_unitario = ET.SubElement(detalle_element, 'precioUnitario')
            precio_unitario.text = str(detalle.precio_unitario)
            descuento = ET.SubElement(detalle_element, 'descuento')
            descuento.text = '0.00'
            precio_total_sin_impuesto = ET.SubElement(
                detalle_element, 'precioTotalSinImpuesto')
            precio_total_sin_impuesto.text = str(detalle.subtotal_producto)

            detalles_adicionales = ET.SubElement(
                detalle_element, 'detallesAdicionales')
            det_adicional = ET.SubElement(detalles_adicionales, 'detAdicional')
            det_adicional.set('nombre', 'informacionAdicional')
            det_adicional.set('valor', Producto.objects.get(
                id_producto=detalle.id_producto_per).producto)

            impuestos = ET.SubElement(detalle_element, 'impuestos')
            impuesto = ET.SubElement(impuestos, 'impuesto')
            codigo = ET.SubElement(impuesto, 'codigo')
            codigo.text = '2'
            codigo_porcentaje = ET.SubElement(impuesto, 'codigoPorcentaje')
            codigo_porcentaje.text = '0' if detalle.total_iva == 0.00 else '2'

            tarifa = ET.SubElement(impuesto, 'tarifa')
            tarifa.text = str(detalle.total_iva)
            base_imponible = ET.SubElement(impuesto, 'baseImponible')
            base_imponible.text = str(detalle.subtotal_producto)
            valor = ET.SubElement(impuesto, 'valor')
            valor.text = str(detalle.total_iva)

        contenido_xml_bytes = ET.tostring(factura, encoding='UTF-8')
        contenido_xml_str = contenido_xml_bytes.decode('UTF-8')
        contenido_xml = '<?xml version="1.0" encoding="UTF-8"?>\n' + contenido_xml_str

        return contenido_xml

    def firmar_xml(self, xml_data, factura):
        empresa = Empresa.objects.filter(id_empresa=Usuario.objects.filter(
            id_usuario=factura.id_usuario_per).values('id_empresa_per').first()['id_empresa_per']).first()
        # cliente = Cliente.objects.get(id_cliente=factura.id_cliente_per)
        clave_p12_path = empresa.firma_electronica.path
        clave_p12_password = empresa.contrasena_firma_electronica

        try:
            with open(clave_p12_path, 'rb') as f:
                p12_data = f.read()
            p12 = pkcs12.load_key_and_certificates(
                p12_data, clave_p12_password.encode(), default_backend())

            # Convierte la cadena XML en un elemento XML
            xml_element = ET.fromstring(xml_data)

            cert = p12[1]  # Obtener el certificado de la lista

            # Lee el archivo PKCS12 y obtén la clave privada y el certificado
            with open(clave_p12_path, 'rb') as clave_p12_file:
                p12 = serialization.pkcs12.load_key_and_certificates(
                    clave_p12_file.read(),
                    clave_p12_password.encode('utf-8')
                )
                clave_privada = p12[0]
                # clave_privada=clave_privada.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)
                # Obtener el certificado de la lista
                certificado = p12[1].public_bytes(serialization.Encoding.PEM)
                # certificado=certificado.public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)

            # Firma el elemento XML
            signed_xml_element = XMLSigner().sign(
                xml_element, key=clave_privada, cert=certificado)

            # Convierte el elemento XML firmado en una cadena XML
            signed_xml = ET.tostring(signed_xml_element, encoding='UTF-8')

            return signed_xml.decode('UTF-8')
        except InvalidSignature:
            # Manejar la excepción de firma no válida
            return None

    def validar_xml(self, signed_xml):
        # Ruta del archivo WSDL
        wsdl_url = 'https://celcer.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantesOffline?wsdl'
        # wsdl_url = 'https://celcer.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantesOffline?wsdl'

        # Crear un cliente SOAP a partir del archivo WSDL
        client = Client(wsdl_url)

        # Codificar el contenido XML en base64
        xml_bytes = signed_xml.encode('utf-8')
        xml_base64 = base64.b64encode(xml_bytes).decode('utf-8')

        # Llamar al método "validarComprobante" del servicio web
        response = client.service.validarComprobante(xml_base64)

        # Procesar la respuesta del servicio web
        # estado = response.estado
        # Acceder a la lista de comprobantes
        comprobantes = response.comprobantes.comprobante

        # Verificar si la lista de comprobantes está vacía
        if not comprobantes:
            # Retornar mensaje de validación exitosa
            return HttpResponse("Validación exitosa")

        # Crear una lista para almacenar los resultados
        resultados = []

        # Agregar el estado y los detalles de cada comprobante a la lista de resultados
        for comprobante in comprobantes:
            clave_acceso = comprobante.claveAcceso
            mensajes = comprobante.mensajes
            detalles = []
            for mensaje in mensajes:
                # Acceder al identificador dentro de la tupla
                identificador = mensaje[0]
                # Acceder al mensaje dentro de la tupla
                mensaje_texto = mensaje[1]
                detalles.append(
                    {'identificador': identificador, 'mensaje': mensaje_texto})
            resultados.append(
                {'clave_acceso': clave_acceso, 'detalles': detalles})

        # Retornar la lista de resultados
        return HttpResponse(resultados)

    def generar_clave_acceso(self, fecha_emision, tipo_comprobante, ruc, ambiente, serie, numero_comprobante, codigo_numerico, tipo_emision):
        # Obtener fecha actual
        fecha_actual = date.today().strftime('%d%m%Y')

        # Generar clave de acceso incompleta
        clave_acceso_incompleta = fecha_emision + tipo_comprobante + ruc + \
            ambiente + serie + numero_comprobante + codigo_numerico + tipo_emision

        # Calcular dígito verificador
        digito_verificador = str(self.getMod11Dv(clave_acceso_incompleta))

        # Construir clave de acceso completa
        clave_acceso = clave_acceso_incompleta + digito_verificador

        return clave_acceso

    def enviar_comprobante_correo(self, documento, factura):
        try:
            cliente = Cliente.objects.get(id_cliente=factura.id_cliente_per)
            if cliente.correo is not None and cliente.numero_identificacion != '9999999999999':
                message = MIMEMultipart("alternative")
                message["Subject"] = "EasyFact: Tu factura está disponible"
                message["From"] = "easyfact.gc@gmail.com"
                message["To"] = cliente.correo

                # Carga de Docuemntos
                html_file = 'static/email/plantilla/template.html'
                pdf_file = documento.ride.path
                xml_file = documento.xml.path

                with open(html_file, 'r') as file:
                    html = file.read()
                    html_attachment = MIMEText(html, 'html')

                with open(pdf_file, 'rb') as file:
                    pdf_attachment = MIMEApplication(file.read())

                with open(xml_file, 'rb') as file:
                    xml_attachment = MIMEApplication(file.read())

                # html_mime = MIMEText(html, 'html')
                pdf_attachment.add_header(
                    'Content-Disposition', 'attachment', filename=pdf_file)
                xml_attachment.add_header(
                    'Content-Disposition', 'attachment', filename=xml_file)

                message.attach(html_attachment)
                message.attach(pdf_attachment)
                message.attach(xml_attachment)

                context = ssl.create_default_context()

                smtp_address = "smtp.gmail.com"
                smtp_port = 465
                email_address = "easyfact.gc@gmail.com"
                email_password = "xckircpskzjnfkgk"
                email_receiver = cliente.correo

                with smtplib.SMTP_SSL(smtp_address, smtp_port, context=context) as server:
                    server.login(email_address, email_password)
                    server.sendmail(
                        email_address, email_receiver, message.as_string())
        except Exception as e:
            print('Error al enviar el correo: ', e)

    def guardar_comprobantes(self, pdf, xml, clave_acceso):
        # Obtener las rutas de los directorios
        xml_directory = os.path.join('static', 'email', 'xml')

        # Verificar si los directorios existen, si no, crearlos
        os.makedirs(xml_directory, exist_ok=True)

        # Generar los nombres de los archivos
        xml_filename = f"factura_{clave_acceso}.xml"

        # Guardar los archivos en las rutas especificadas
        xml_path = os.path.join(xml_directory, xml_filename)

        with open(xml_path, 'w') as xml_file:
            xml_file.write(xml)

        # Guardar las rutas en la base de datos
        comprobante = Documento.objects.create(
            ride=pdf,
            xml=xml_path,
        )

        Factura.objects.filter(clave_acceso=clave_acceso).update(
            id_documento_per=comprobante.id_documento
        )

        return comprobante


    def getMod11Dv(self, num):
        digits = num[::-1].replace('.', '').replace(',', '')
        if not digits.isdigit():
            return False
        sum = 0
        factor = 2
        for i in range(len(digits)):
            sum += int(digits[i]) * factor
            if factor == 7:
                factor = 2
            else:
                factor += 1
        dv = 11 - (sum % 11)
        if dv == 10:
            return 1
        if dv == 11:
            return 0
        return dv


class FormaPagoView(View):          
    def get(self, request, id_forma_pago=None):
        try:
            if id_forma_pago is not None:
                forma_pago = Forma_pago.objects.filter(id_forma_pago=id_forma_pago).values()
                datos= {"Forma_pago": list(forma_pago)}
            else:
                formas_pago = Forma_pago.objects.filter().values()
                datos= {"Formas_pago": list(formas_pago)}
        except :
            datos= {"Formas_pago": []}
        return JsonResponse(datos)
    

class ProductoEstrellaView(View):
    def get(self, request, id_empresa=None):
        if id_empresa is not None:
            fecha_inicio = date.today() - timedelta(days=30)
            producto_mas_vendido = Detalle_factura.objects.filter(
                id_factura_per__id_usuario_per__id_empresa_per=id_empresa,
                id_factura_per__fecha__range=[fecha_inicio, date.today()]
            ).values('id_producto_per').annotate(
                total_vendido=Sum('cantidad')
            ).order_by('-total_vendido').first()

            if producto_mas_vendido:
                id_producto = producto_mas_vendido['id_producto_per']
                unidades_vendidas = producto_mas_vendido['total_vendido']
                producto = Producto.objects.get(id_producto=id_producto)
                datos = {
                    'producto': producto.producto,
                    'id_producto': id_producto,
                    'unidades_vendidas': unidades_vendidas
                }
            else:
                datos= NOT_DATA_MESSAGE
        else:
            datos= NOT_DATA_MESSAGE

        return JsonResponse(datos)