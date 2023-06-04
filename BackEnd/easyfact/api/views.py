from typing import Any
from django import http
from django.http import JsonResponse
from django.views import View
from .models import Usuario
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json

# Create your views here.
class UsuarioVista(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, id_usuario=0):
        if id_usuario > 0:
            usuarios = list(Usuario.objects.filter(id_usuario=id_usuario).values())
            if len(usuarios) > 0:
                usuario = usuarios[0]
                datos = {'mesaje': 'Success', 'usuario': usuario}
            else:
                datos = {'mesaje': 'No hay datos'}
            return JsonResponse(datos)
        else:
            usuarios = list(Usuario.objects.values())
            if len(usuarios) > 0:
                datos = {'mesaje': 'Success', 'usuarios': usuarios}
            else:
                datos = {'mesaje': 'No hay datos'}
            return JsonResponse(datos)
    
    def post(self, request):
        jsonData = json.loads(request.body)
        Usuario.objects.create(
            id_empresa_per=jsonData['id_empresa_per'], correo=jsonData['correo'], nombre=jsonData['nombre'], apellido=jsonData['apellido'], contrasena=jsonData['contrasena'])
        datos = {'mensaje': 'Success'}
        return JsonResponse(datos)