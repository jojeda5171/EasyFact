from django.urls import path
# from .views import CompanyView
from .views import UsuarioVista, EmpresaVista, LogoVista, FirmaVista, IvaVista, ProductoVista, IconoProductoVista, ClienteVista, LicenciaVista, IvaProductoVista, AbrirFacturaView, AgregarProductoView, CerrarFacturaView, MostrarFacturaView, FormaPagoView, ProductoEstrellaView, ClienteEstrellaView, MostrarDetalleFacturaView

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
    path('iva/<str:id_empresa>/<str:id_iva>/',
         IvaVista.as_view(), name='iva_proceso'),
    path('producto/', ProductoVista.as_view(), name='producto_lista'),
    path('producto/<str:id_empresa>/', ProductoVista.as_view(), name='producto_proceso'),
    path('producto/<str:id_empresa>/<str:id_producto>/', ProductoVista.as_view(), name='producto_proceso'),
    path('productoiva/<str:ruc>/<str:producto>/', IvaProductoVista.as_view(), name='producto_proceso'), #editar el producto con el iva
    path('productoicono/<str:ruc>/<str:producto>/', IconoProductoVista.as_view(), name='icono_producto_proceso'),
    path('cliente/<str:id_cliente>/<str:id_empresa>/', ClienteVista.as_view(), name='cliente_proceso'),#get ciente de una empresa
    path('cliente/<str:id_empresa>/', ClienteVista.as_view(), name='cliente'),
    path('licencia/<str:ruc>/', LicenciaVista.as_view(), name='licencia_proceso'),
    path('abrirfactura/', AbrirFacturaView.as_view(), name='abrirfactura_proceso'),
    path('abrirfactura/<str:id_factura>/', AbrirFacturaView.as_view(), name='abrirfactura_proceso'),
    path('agregarproducto/', AgregarProductoView.as_view(), name='agregarproducto_proceso'),
    path('agregarproducto/<str:id_detalle_factura>/', AgregarProductoView.as_view(), name='agregarproducto_proceso'),
    path('mostrardetallefactura/<str:id_factura>/', MostrarDetalleFacturaView.as_view(), name='mostrardetallefactura_proceso'),
    path('cerrarfactura/', CerrarFacturaView.as_view(), name='cerrarfactura_proceso'),
    path('verFacturas/<str:id_empresa>/', MostrarFacturaView.as_view(), name='verFacturas_proceso'),
    path('formapago/', FormaPagoView.as_view(), name='formapago_lista'),
    path('formapago/<str:id_forma_pago>/', FormaPagoView.as_view(), name='formapago_proceso'),
    path('productoestrella/<str:id_empresa>/', ProductoEstrellaView.as_view(), name='productoestrella_proceso'),
    path('clienteestrella/<str:id_empresa>/', ClienteEstrellaView.as_view(), name='clienteestrella_proceso'),
]
