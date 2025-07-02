from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.db.models import Q
from .models import CuentaContable, AsientoContable
from .forms import CuentaContableForm, AsientoContableForm, MovimientoContableFormSet
from django.views import View
from django.shortcuts import render, redirect
from django.db import transaction
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.views.generic.detail import DetailView
import json
from django.db.models.deletion import ProtectedError
from django.contrib import messages

class CuentaContableListView(ListView):
    """Vista para listar cuentas contables con búsqueda y soporte HTMX."""
    model = CuentaContable
    template_name = 'asientos_contables/cuentas/list.html'
    context_object_name = 'cuentas'

    def get_queryset(self):
        qs = super().get_queryset().order_by('created_at')
        q = self.request.GET.get("q", "")
        if q:
            qs = qs.filter(Q(codigo__icontains=q) | Q(nombre__icontains=q))
        return qs

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get("Hx-Request") == "true":
            # Solo la tabla (partial)
            html = render_to_string(
                'asientos_contables/cuentas/partials/list_items.html',
                context,
                request=self.request
            )
            
            return HttpResponse(html)
        # Página completa
        return super().render_to_response(context, **response_kwargs)

class CuentaContableCreateView(CreateView):
    """Vista para crear una cuenta contable (modal HTMX)."""
    model = CuentaContable
    form_class = CuentaContableForm
    template_name = 'asientos_contables/cuentas/partials/form.html'

    def form_valid(self, form):
        self.object = form.save()
        cuentas = self.model.objects.all()
        html_tabla = render_to_string(
            'asientos_contables/cuentas/partials/list_items.html',
            {'cuentas': cuentas},
            request=self.request
        )
        # OOB: actualiza la tabla y cierra el modal
        html_oob = (
            '<div id="cuentas-table" hx-swap-oob="innerHTML">'
            f'{html_tabla}'
            '</div>'
            '<div id="modal-body" hx-swap-oob="innerHTML"></div>'
            '<script>closeModal();</script>'
        )
        return HttpResponse(html_oob)

    def form_invalid(self, form):
        # Si hay errores, solo devuelve el formulario con errores
        return self.render_to_response(self.get_context_data(form=form))

class CuentaContableUpdateView(UpdateView):
    """Vista para editar una cuenta contable (modal HTMX)."""
    model = CuentaContable
    form_class = CuentaContableForm
    template_name = 'asientos_contables/cuentas/partials/form.html'

    def form_valid(self, form):
        self.object = form.save()
        cuentas = self.model.objects.all()
        html_tabla = render_to_string(
            'asientos_contables/cuentas/partials/list_items.html',
            {'cuentas': cuentas},
            request=self.request
        )
        # OOB: actualiza la tabla y cierra el modal
        html_oob = (
            '<div id="cuentas-table" hx-swap-oob="innerHTML">'
            f'{html_tabla}'
            '</div>'
            '<div id="modal-body" hx-swap-oob="innerHTML"></div>'
            '<script>closeModal();</script>'
        )
        return HttpResponse(html_oob)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

class CuentaContableDeleteView(DeleteView):
    """Vista para eliminar una cuenta contable (modal HTMX)."""
    model = CuentaContable
    template_name = 'asientos_contables/cuentas/partials/delete_confirm.html'

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            self.object.delete()
            # Redirige o responde con éxito
            return redirect('asientos_contables:cuenta_list')
        except ProtectedError:
            # Muestra un mensaje de error
            messages.error(request, "No se puede eliminar la cuenta porque tiene movimientos asociados.")
            return self.get(request, *args, **kwargs)

# --- NUEVA VISTA PARA CREAR ASIENTO CONTABLE ---

class AsientoContableListView(ListView):
    """Vista para listar asientos contables con búsqueda y soporte HTMX."""
    model = AsientoContable
    template_name = 'asientos_contables/asientos/list.html'
    context_object_name = 'asientos'

    def get_queryset(self):
        qs = super().get_queryset().order_by('-created_at')
        q = self.request.GET.get('q', '')
        if q:
            qs = qs.filter(descripcion__icontains=q)
        return qs

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get("Hx-Request") == "true":
            html = render_to_string(
                'asientos_contables/asientos/partials/list_items.html',
                context,
                request=self.request
            )
            return HttpResponse(html)
        return super().render_to_response(context, **response_kwargs)

class AsientoContableCreateView(View):
    """Vista para crear un asiento contable con movimientos dinámicos y validación de balanceo."""
    model = AsientoContable
    form_class = AsientoContableForm
    template_name = 'asientos_contables/asientos/partials/form.html'

    def get(self, request):
        form = AsientoContableForm()
        formset = MovimientoContableFormSet()
        return render(request, self.template_name, {
            'form': form,
            'formset': formset,
        })

    def post(self, request):
        form = AsientoContableForm(request.POST)
        formset = MovimientoContableFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            # Validación de balance
            total_debe = sum((f.cleaned_data.get('debe') or 0) for f in formset.forms if not f.cleaned_data.get('DELETE', False))
            total_haber = sum((f.cleaned_data.get('haber') or 0) for f in formset.forms if not f.cleaned_data.get('DELETE', False))
            print("Total debe:", total_debe, "Total haber:", total_haber)
            if total_debe != total_haber:
                print("Error: Debe y haber no cuadran")
                formset._non_form_errors = formset._non_form_errors or []
                formset._non_form_errors.append("La suma del debe debe ser igual a la suma del haber.")
                return render(request, 'asientos_contables/asientos/partials/form.html', {
                    'form': form,
                    'formset': formset,
                })
            with transaction.atomic():
                asiento = form.save()
                movimientos = formset.save(commit=False)
                for mov in movimientos:
                    mov.asiento = asiento
                    mov.save()
            # OOB swap: actualiza la tabla y cierra el modal
            asientos = AsientoContable.objects.all()
            html_tabla = render_to_string(
                'asientos_contables/asientos/partials/list_items.html',
                {'asientos': asientos},
                request=request
            )
            html_oob = (
                '<div id="asientos-table" hx-swap-oob="innerHTML">'
                f'{html_tabla}'
                '</div>'
                '<div id="modal-body" hx-swap-oob="innerHTML"></div>'
                '<script>closeModal();</script>'
            )
            print("Guardado exitoso, OOB swap enviado")
            return HttpResponse(html_oob)
        # Si hay errores, renderiza el form con errores
        print("Renderizando form con errores")
        return render(request, 'asientos_contables/asientos/partials/form.html', {
            'form': form,
            'formset': formset,
        })

class AsientoContableDetailView(DetailView):
    """Vista para mostrar el detalle de un asiento contable en modal."""
    model = AsientoContable
    template_name = 'asientos_contables/asientos/partials/detail.html'
    context_object_name = 'asiento'
