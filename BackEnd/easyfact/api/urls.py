from django.urls import path
# from .views import CompanyView
from .views import UsuarioVista, EmpresaVista, LogoVista, FirmaVista, IvaVista, ProductoVista, IconoProductoVista, ClienteVista, LicenciaVista, IvaProductoVista

urlpatterns = [
    path('usuario/', UsuarioVista.as_view(), name='usuario_lista'),
    path('usuario/<str:correo>/<str:contrasena>/',
         UsuarioVista.as_view(), name='usuario_proceso'),
    path('empresa/', EmpresaVista.as_view(), name='empresa_lista'),
    path('empresa/<str:ruc>/', EmpresaVista.as_view(), name='empresa_proceso'),
    path('logoempresa/<str:ruc>/', LogoVista.as_view(),
         name='logoempresa_proceso'),
    path('firmaempresa/<str:ruc>/', FirmaVista.as_view(),
         name='firmaempresa_proceso'),
    path('iva/<str:ruc>/', IvaVista.as_view(), name='iva_lista'),
    path('iva/<str:ruc>/<str:iva_nombre>/',
         IvaVista.as_view(), name='iva_proceso'),
    path('producto/', ProductoVista.as_view(), name='producto_lista'),
    path('producto/<str:ruc>/', ProductoVista.as_view(), name='producto_proceso'),
    path('producto/<str:ruc>/<str:producto>/', ProductoVista.as_view(), name='producto_proceso'),
    path('productoiva/<str:ruc>/<str:producto>/', IvaProductoVista.as_view(), name='producto_proceso'), #editar el producto con el iva
    path('productoicono/<str:ruc>/<str:producto>/', IconoProductoVista.as_view(), name='icono_producto_proceso'),
    path('cliente/<str:numero_identificacion>/<str:ruc>/', ClienteVista.as_view(), name='cliente_proceso'),#get ciente de una empresa
    path('cliente/<str:ruc>/', ClienteVista.as_view(), name='cliente'),
    path('licencia/<str:ruc>/', LicenciaVista.as_view(), name='licencia_proceso')
]
