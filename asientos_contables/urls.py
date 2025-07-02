from django.urls import path
from .views import (
    CuentaContableListView,
    CuentaContableCreateView,
    CuentaContableUpdateView,
    CuentaContableDeleteView,
    AsientoContableCreateView,
    AsientoContableListView,
    AsientoContableDetailView,
)

app_name = "asientos_contables"

urlpatterns = [
    # La raíz de la app será la lista de cuentas
    path('cuentas/', CuentaContableListView.as_view(), name='cuenta_list'),
    path('cuentas/nueva/', CuentaContableCreateView.as_view(), name='cuenta_create'),
    path('cuentas/<int:pk>/editar/', CuentaContableUpdateView.as_view(), name='cuenta_update'),
    path('cuentas/<int:pk>/eliminar/', CuentaContableDeleteView.as_view(), name='cuenta_delete'),

    # Asientos
    path('asientos/', AsientoContableListView.as_view(), name='asiento_list'),
    path('asientos/nuevo/', AsientoContableCreateView.as_view(), name='asiento_create'),
    path('asientos/<int:pk>/ver/', AsientoContableDetailView.as_view(), name='asiento_detail'),
]
