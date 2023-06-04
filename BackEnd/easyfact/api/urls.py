from django.urls import path
#from .views import CompanyView
from .views import UsuarioVista

urlpatterns = [
    path('usuario/', UsuarioVista.as_view(), name='usuario_lista'),
    path('usuario/<int:id_usuario>', UsuarioVista.as_view(), name='usuario_proceso'),
]