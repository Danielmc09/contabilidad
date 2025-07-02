from django.db import models
from django.db.models import Sum, F, DecimalField
from django.db.models.functions import Coalesce
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from decimal import Decimal

class TimeStampedModel(models.Model):
    """
    Modelo base abstracto que añade campos de fecha de creación y actualización.
    """
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")

    class Meta:
        abstract = True


class CuentaContable(TimeStampedModel):
    """
    Modelo que representa una cuenta del plan contable.
    Ejemplo: Caja, Banco, Ventas, Gastos.
    """
    codigo = models.CharField(
        max_length=20,
        unique=True,
        error_messages={
            "unique": "Ya existe una cuenta contable con este código."
        }
    )
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)

    class Meta:
        ordering = ['codigo']
        verbose_name = "Cuenta contable"
        verbose_name_plural = "Cuentas contables"

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class AsientoContableManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().annotate(
            total_debe_annotated=Sum(F('movimientos__debe'), output_field=DecimalField(max_digits=12, decimal_places=2)),
            total_haber_annotated=Sum(F('movimientos__haber'), output_field=DecimalField(max_digits=12, decimal_places=2))
        )


class AsientoContable(TimeStampedModel):
    """
    Modelo que representa un asiento contable, agrupando movimientos.
    """
    fecha = models.DateField()
    descripcion = models.TextField()
    
    objects = AsientoContableManager()

    class Meta:
        ordering = ['-fecha']
        verbose_name = "Asiento contable"
        verbose_name_plural = "Asientos contables"

    def __str__(self):
        return f"Asiento del {self.fecha} - {self.descripcion[:40]}"

    def clean(self):
        """
        Valida que el asiento esté balanceado (debe == haber).
        """
        if not self.pk:
            return  # No validar aún si el asiento no ha sido guardado

        total_debe = sum((m.debe or Decimal('0.00')) for m in self.movimientos.all())
        total_haber = sum((m.haber or Decimal('0.00')) for m in self.movimientos.all())
        if total_debe != total_haber:
            raise ValidationError(
                _("El asiento contable no está balanceado: debe (%(debe)s) ≠ haber (%(haber)s)."),
                code="asiento_no_balanceado",
                params={"debe": total_debe, "haber": total_haber},
            )

    def total_debe(self):
        """Suma total del debe de todos los movimientos."""
        return sum((m.debe or Decimal('0.00')) for m in self.movimientos.all())

    def total_haber(self):
        """Suma total del haber de todos los movimientos."""
        return sum((m.haber or Decimal('0.00')) for m in self.movimientos.all())

    def movimientos_count(self):
        """Cantidad de movimientos asociados al asiento."""
        return self.movimientos.count()

    def esta_balanceado(self):
        """Indica si el asiento está balanceado (debe == haber)."""
        # Use annotated fields if available, otherwise fall back to method calls
        if hasattr(self, 'total_debe_annotated') and hasattr(self, 'total_haber_annotated'):
            return (self.total_debe_annotated or Decimal('0.00')) == (self.total_haber_annotated or Decimal('0.00'))
        return self.total_debe() == self.total_haber()


class MovimientoContable(models.Model):
    """
    Modelo que representa un movimiento contable (línea de asiento).
    """
    asiento = models.ForeignKey(
        AsientoContable,
        on_delete=models.CASCADE,
        related_name="movimientos"
    )
    cuenta = models.ForeignKey(CuentaContable, on_delete=models.PROTECT)
    debe = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    haber = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    class Meta:
        verbose_name = "Movimiento contable"
        verbose_name_plural = "Movimientos contables"

    def __str__(self):
        signo = "Debe" if self.debe else "Haber"
        valor = self.debe or self.haber
        return f"{self.cuenta.codigo} | {signo}: {valor}"

    def clean(self):
        """
        Valida que solo uno de debe/haber tenga valor y que no estén ambos vacíos.
        """
        if self.debe and self.haber:
            raise ValidationError(_("Un movimiento no puede tener valores en ambos campos (debe y haber)."))

        if not self.debe and not self.haber:
            raise ValidationError(_("Debe ingresar un valor en debe o haber."))
