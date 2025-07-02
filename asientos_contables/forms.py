from django import forms
from .models import CuentaContable, AsientoContable, MovimientoContable
from django.forms.models import inlineformset_factory, BaseInlineFormSet
from decimal import Decimal

class CuentaContableForm(forms.ModelForm):
    """Formulario para crear/editar cuentas contables."""
    class Meta:
        model = CuentaContable
        fields = ['codigo', 'nombre', 'descripcion']
        widgets = {
            'codigo': forms.TextInput(attrs={'autofocus': 'autofocus'}),
            'descripcion': forms.Textarea(attrs={'rows': 2}),
        }

class AsientoContableForm(forms.ModelForm):
    """Formulario para crear/editar asientos contables."""
    class Meta:
        model = AsientoContable
        fields = ['fecha', 'descripcion']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'descripcion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej. Pago de nómina julio',
            }),
        }

class MovimientoContableForm(forms.ModelForm):
    """Formulario para crear/editar movimientos contables."""
    class Meta:
        model = MovimientoContable
        fields = ['cuenta', 'debe', 'haber']
        widgets = {
            'cuenta': forms.Select(attrs={'class': 'form-control'}),
            'debe': forms.NumberInput(attrs={
                'class': 'form-control text-end',
                'step': '0.01',
                'placeholder': 'Ej. 1000.00',
            }),
            'haber': forms.NumberInput(attrs={
                'class': 'form-control text-end',
                'step': '0.01',
                'placeholder': 'Ej. 1000.00',
            }),
        }

class BaseMovimientoContableFormSet(BaseInlineFormSet):
    """
    FormSet para Movimientos Contables con validación de balanceo.
    """
    def clean(self):
        super().clean()

        # No hacer nada si hay otros errores de validación individuales
        if any(self.errors):
            return

        total_debe = Decimal('0.00')
        total_haber = Decimal('0.00')

        for form in self.forms:
            # Ignorar formularios vacíos o marcados para eliminación
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                total_debe += form.cleaned_data.get('debe') or Decimal('0.00')
                total_haber += form.cleaned_data.get('haber') or Decimal('0.00')

        if total_debe != total_haber:
            raise forms.ValidationError(
                "El asiento no está balanceado. Total Debe: %(debe)s vs Total Haber: %(haber)s.",
                code='asiento_no_balanceado',
                params={'debe': total_debe, 'haber': total_haber}
            )

MovimientoContableFormSet = inlineformset_factory(
    AsientoContable,
    MovimientoContable,
    form=MovimientoContableForm,
    formset=BaseMovimientoContableFormSet,
    extra=2,
    can_delete=True
)