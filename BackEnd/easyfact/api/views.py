from .constants import SUCCESS_MESSAGE, ERROR_MESSAGE, NOT_DATA_MESSAGE
from django.http import JsonResponse, HttpResponse, FileResponse
from django.core.files.storage import default_storage
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import Usuario, Empresa, Licencia
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
            id_empresa_per = Empresa.objects.get(ruc=jsonData['id_empresa_per']).id_empresa
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
                usuario = Usuario.objects.get(correo=correo, contrasena=contrasena)
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
                Usuario.objects.filter(correo=correo, contrasena=contrasena).delete()
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
            empresas=Empresa.objects.filter(ruc=ruc).values()
            if len(empresas)>0:
                empresa=empresas[0]
                datos={'empresa':empresa}
            else:
                datos=NOT_DATA_MESSAGE
        else:
            empresas=list(Empresa.objects.values())
            if len(empresas)>0:
                datos={'empresas': empresas}
            else:
                datos=NOT_DATA_MESSAGE
        return JsonResponse(datos)

    def post(self, request):
        try:
            jsonData = json.loads(request.body)
            imagen = request.FILES.get('logo')
            firma=request.FILES.get('firma_electronica')
            img_path = os.path.join('logo', imagen.name)
            img_path = default_storage.save(img_path, imagen)
            firma_path=os.path.join('firma_electronica', firma.name)
            firma_path=default_storage.save(firma_path, firma)
            Empresa.objects.create(
                licencia_per=jsonData['licencia_per'],
                ruc=jsonData['ruc'],
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
                empresa=Empresa.objects.get(ruc=ruc)
                empresa.licencia_per=jsonData['licencia_per']
                empresa.ruc=jsonData['ruc']
                empresa.razon_social=jsonData['razon_social']
                empresa.nombre_comercial=jsonData['nombre_comercial']
                empresa.direccion=jsonData['direccion']
                empresa.telefono=jsonData['telefono']
                empresa.lleva_contabilidad=jsonData['lleva_contabilidad']
                empresa.contrasena_firma_electronica=jsonData['contrasena_firma_electronica']
                empresa.desarrollo=jsonData['desarrollo']
                empresa.save()
                datos=SUCCESS_MESSAGE
            else:
                datos=NOT_DATA_MESSAGE
        except Exception as e:
            datos=ERROR_MESSAGE
        return JsonResponse(datos)
        
    def delete(self, request, ruc=None):
        try:
            if Empresa.objects.filter(ruc=ruc).exists():
                Empresa.objects.filter(ruc=ruc).delete()
                datos=SUCCESS_MESSAGE
            else:
                datos=NOT_DATA_MESSAGE
        except Exception as e:
            datos=ERROR_MESSAGE
        return JsonResponse(datos)

class LogoVista(View):
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

class FirmaVista(View):
    def get(self, request, ruc=None):
        try:
            empresa = Empresa.objects.get(ruc=ruc)
            firma_path = empresa.firma_electronica.path
            nombre_archivo = os.path.basename(firma_path)
            response = FileResponse(open(firma_path, 'rb'))
            response['Content-Disposition'] = 'attachment; filename="{}"'.format(nombre_archivo)
            return response
        except Empresa.DoesNotExist:
            datos = ERROR_MESSAGE
        except Exception as e:
            datos = ERROR_MESSAGE
        return JsonResponse(datos)

class LicenciaView(View):
    def get(self, request, licencia=None):
        jsonData=json.loads(request.body)
        return {'licencia': list(Licencia.objects.filter(licencia=licencia).values()[0])}
