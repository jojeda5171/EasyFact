from .constants import SUCCESS_MESSAGE, ERROR_MESSAGE, NOT_DATA_MESSAGE
from django.http import JsonResponse, HttpResponse, FileResponse
from django.core.files.storage import default_storage
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import Usuario, Empresa, Iva, Detalle_empresa_iva, Producto, Detalle_empresa_producto, Cliente, Detalle_empresa_cliente, Licencia
from django.db import IntegrityError
from django.views import View
import json
import os

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
                empresa = Empresa.objects.get(ruc=jsonData['id_empresa_per'])
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

    def get(self, request, ruc=None):
        if ruc is not None:
            empresas = Empresa.objects.filter(ruc=ruc).values()
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

    def put(self, request, ruc=None):
        try:
            jsonData = json.loads(request.body)
            if Empresa.objects.filter(ruc=ruc).exists():
                empresa = Empresa.objects.get(ruc=ruc)
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

    def delete(self, request, ruc=None):
        try:
            if Empresa.objects.filter(ruc=ruc).exists():
                Empresa.objects.filter(ruc=ruc).delete()
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

    def get(self, request, ruc=None):
        try:
            empresa = Empresa.objects.get(ruc=ruc)
            imagen_path = empresa.logo.path
            with open(imagen_path, 'rb') as file:
                response = HttpResponse(file.read(), content_type='image/jpeg')
                return response
        except Empresa.DoesNotExist:
            datos = ERROR_MESSAGE
        except Exception as e:
            datos = ERROR_MESSAGE
        return JsonResponse(datos)

    def post(self, request, ruc=None):
        try:
            empresa = Empresa.objects.get(ruc=ruc)
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

    def get(self, request, ruc=None):
        try:
            empresa = Empresa.objects.get(ruc=ruc)
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

    def post(self, request, ruc=None):
        try:
            empresa = Empresa.objects.get(ruc=ruc)
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

    def get(self, request, ruc=None, iva_nombre=None):
        try:
            if iva_nombre is not None:
                id_empresa = Empresa.objects.get(ruc=ruc).id_empresa
                iva = list(Iva.objects.filter(id_iva__in=Detalle_empresa_iva.objects.filter(
                    id_empresa_per=id_empresa).values('id_iva_per'), iva_nombre=iva_nombre).values())
                if len(iva) > 0:
                    datos = {'iva': iva[0]}
                else:
                    datos = NOT_DATA_MESSAGE
            else:
                id_empresa = Empresa.objects.get(ruc=ruc).id_empresa
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

    def post(self, request, ruc=None):
        try:
            jsonData = json.loads(request.body)
            id_empresa = Empresa.objects.get(ruc=ruc).id_empresa
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

    def put(self, request, ruc=None, iva_nombre=None):
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

    def delete(self, request, ruc=None, iva_nombre=None):
        try:
            id_empresa = Empresa.objects.get(ruc=ruc).id_empresa
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

    def get(self, request, ruc=None, producto=None):
        try:
            id_empresa = Empresa.objects.get(ruc=ruc).id_empresa
            if producto is not None:
                producto = list(Producto.objects.filter(id_producto__in=Detalle_empresa_producto.objects.filter(
                    id_empresa_per=id_empresa).values('id_producto_per'), producto=producto).values())
                if len(producto) > 0:
                    datos = {'producto': producto[0]}
                else:
                    datos = NOT_DATA_MESSAGE
            else:
                id_empresa = Empresa.objects.get(ruc=ruc).id_empresa
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

    def post(self, request, ruc=None):
        try:
            empresa = Empresa.objects.get(ruc=ruc).id_empresa
            jsonData = request.POST
            icono = request.FILES.get('icono')
            img_path = os.path.join('static', 'iconos', icono.name)
            img_path = default_storage.save(img_path, icono)
            with open(img_path, 'wb') as f:
                for chunk in icono.chunks():
                    f.write(chunk)
            nuevo_producto = Producto.objects.create(
                id_iva_per=Iva.objects.filter(iva_nombre=jsonData['id_iva_per']).values(
                    'id_iva').first()['id_iva'],
                producto=jsonData['producto'],
                icono=img_path,
                precio=jsonData['precio']
            )
            Detalle_empresa_producto.objects.create(
                id_producto_per=nuevo_producto.id_producto,
                id_empresa_per=empresa
            )
            datos = SUCCESS_MESSAGE
        except Exception as e:
            datos = ERROR_MESSAGE
        return JsonResponse(datos)

    def put(self, request, ruc=None, producto=None):
        try:
            jsonData = json.loads(request.body)
            if Producto.objects.filter(producto=producto).exists():
                empresa = Empresa.objects.get(ruc=ruc).id_empresa
                producto = Producto.objects.filter(id_producto__in=Detalle_empresa_producto.objects.filter(
                    id_empresa_per=empresa).values('id_producto_per'), producto=producto).update(producto=jsonData['producto'], precio=jsonData['precio'])
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

    def get(self, request, numero_identificacion=None, ruc=None):
        try:
            if numero_identificacion is not None and Cliente.objects.filter(id_cliente__in=Detalle_empresa_cliente.objects.filter(id_empresa_per=Empresa.objects.get(ruc=ruc).id_empresa).values('id_cliente_per'), numero_identificacion=numero_identificacion).exists():
                cliente = Cliente.objects.filter(id_cliente__in=Detalle_empresa_cliente.objects.filter(id_empresa_per=Empresa.objects.get(
                    ruc=ruc).id_empresa).values('id_cliente_per'), numero_identificacion=numero_identificacion).values().first()
                datos = {'cliente': cliente}
            elif numero_identificacion is None and ruc is not None:
                clientes = list(Cliente.objects.filter(id_cliente__in=Detalle_empresa_cliente.objects.filter(
                    id_empresa_per=Empresa.objects.get(ruc=ruc).id_empresa).values('id_cliente_per')).values())
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

    def post(self, request, ruc):
        try:
            jsonData = json.loads(request.body)
            id_empresa = Empresa.objects.get(ruc=ruc).id_empresa
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
                Cliente.objects.create(
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
                    id_cliente_per=Cliente.objects.last().id_cliente
                )
                datos = SUCCESS_MESSAGE
        except Exception as e:
            datos = ERROR_MESSAGE
        except Empresa.DoesNotExist:
            datos = ERROR_MESSAGE
        return JsonResponse(datos)

    def put(self, request, numero_identificacion=None, ruc=None):
        try:
            jsonData = json.loads(request.body)
            if Cliente.objects.filter(id_cliente__in=Detalle_empresa_cliente.objects.filter(id_empresa_per=Empresa.objects.get(ruc=ruc).id_empresa).values('id_cliente_per'), numero_identificacion=numero_identificacion).exists():
                Cliente.objects.filter(id_cliente__in=Detalle_empresa_cliente.objects.filter(id_empresa_per=Empresa.objects.get(ruc=ruc).id_empresa).values('id_cliente_per'), numero_identificacion=numero_identificacion).update(
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

    def delete(self, request, numero_identificacion=None, ruc=None):
        try:
            id_empresa = Empresa.objects.get(ruc=ruc).id_empresa
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
