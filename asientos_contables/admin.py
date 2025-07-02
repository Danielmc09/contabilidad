from django.contrib import admin
from .models import CuentaContable, AsientoContable, MovimientoContable

@admin.register(CuentaContable)
class CuentaContableAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre')
    search_fields = ('codigo', 'nombre')
    ordering = ('codigo',)


class MovimientoContableInline(admin.TabularInline):
    model = MovimientoContable
    extra = 1


@admin.register(AsientoContable)
class AsientoContableAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'descripcion')
    search_fields = ('descripcion',)
    date_hierarchy = 'fecha'
    inlines = [MovimientoContableInline]


@admin.register(MovimientoContable)
class MovimientoContableAdmin(admin.ModelAdmin):
    list_display = ('asiento', 'cuenta', 'debe', 'haber')
    list_filter = ('cuenta',)
