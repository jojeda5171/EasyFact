from django.urls import path
# from .views import CompanyView
from .views import UsuarioVista, EmpresaVista, LogoVista, FirmaVista, IvaVista, ProductoVista, IconoProductoVista, ClienteVista, LicenciaVista, IvaProductoVista, AbrirFacturaView, AgregarProductoView, CerrarFacturaView, MostrarFacturaView

urlpatterns = [
    path('usuario/', UsuarioVista.as_view(), name='usuario_lista'),
    path('usuario/<str:correo>/<str:contrasena>/',
         UsuarioVista.as_view(), name='usuario_proceso'),
    path('empresa/', EmpresaVista.as_view(), name='empresa_lista'),
    path('empresa/<str:id_empresa>/', EmpresaVista.as_view(), name='empresa_proceso'),
    path('logoempresa/<str:id_empresa>/', LogoVista.as_view(),
         name='logoempresa_proceso'),
    path('firmaempresa/<str:id_empresa>/', FirmaVista.as_view(),
         name='firmaempresa_proceso'),
    path('iva/<str:id_empresa>/', IvaVista.as_view(), name='iva_lista'),
    path('iva/<str:id_empresa>/<str:iva_nombre>/',
         IvaVista.as_view(), name='iva_proceso'),
    path('producto/', ProductoVista.as_view(), name='producto_lista'),
    path('producto/<str:id_empresa>/', ProductoVista.as_view(), name='producto_proceso'),
    path('producto/<str:id_empresa>/<str:producto>/', ProductoVista.as_view(), name='producto_proceso'),
    path('productoiva/<str:ruc>/<str:producto>/', IvaProductoVista.as_view(), name='producto_proceso'), #editar el producto con el iva
    path('productoicono/<str:ruc>/<str:producto>/', IconoProductoVista.as_view(), name='icono_producto_proceso'),
    path('cliente/<str:numero_identificacion>/<str:id_empresa>/', ClienteVista.as_view(), name='cliente_proceso'),#get ciente de una empresa
    path('cliente/<str:id_empresa>/', ClienteVista.as_view(), name='cliente'),
    path('licencia/<str:ruc>/', LicenciaVista.as_view(), name='licencia_proceso'),
    path('abrirfactura/', AbrirFacturaView.as_view(), name='abrirfactura_proceso'),
    path('abrirfactura/<str:id_factura>/', AbrirFacturaView.as_view(), name='abrirfactura_proceso'),
    path('agregarproducto/', AgregarProductoView.as_view(), name='agregarproducto_proceso'),
    path('agregarproducto/<str:id_empresa>/', AgregarProductoView.as_view(), name='agregarproducto_proceso'),
    path('cerrarfactura/', CerrarFacturaView.as_view(), name='cerrarfactura_proceso'),
    path('verFacturas/<str:id_empresa>/', MostrarFacturaView.as_view(), name='verFacturas_proceso'),
]
