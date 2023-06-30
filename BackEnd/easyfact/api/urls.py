from django.urls import path
#from .views import CompanyView
from .views import UsuarioVista, EmpresaVista, LogoVista, FirmaVista

urlpatterns = [
    path('usuario/', UsuarioVista.as_view(), name='usuario_lista'),
    path('usuario/<str:correo>/<str:contrasena>/', UsuarioVista.as_view(), name='usuario_proceso'),
    path('empresa/', EmpresaVista.as_view(), name='empresa_lista'),    
    path('empresa/<str:ruc>/', EmpresaVista.as_view(), name='empresa_proceso'),
    path('logoempresa/<str:ruc>/', LogoVista.as_view(), name='logoempresa_proceso'),
    path('firmaempresa/<str:ruc>/', FirmaVista.as_view(), name='firmaempresa_proceso')
    
]