import pytest
from django.urls import reverse
from asientos_contables.models import AsientoContable, MovimientoContable, CuentaContable

@pytest.mark.django_db
def test_crear_asiento_balanceado(client):
    cuenta1 = CuentaContable.objects.create(codigo='100', nombre='Caja')
    cuenta2 = CuentaContable.objects.create(codigo='200', nombre='Banco')

    url = reverse('asientos_contables:asiento_create')
    data = {
        'fecha': '2024-07-01',
        'descripcion': 'Asiento balanceado',
        'movimientos-TOTAL_FORMS': '2',
        'movimientos-INITIAL_FORMS': '0',
        'movimientos-MIN_NUM_FORMS': '0',
        'movimientos-MAX_NUM_FORMS': '1000',
        'movimientos-0-cuenta': cuenta1.pk,
        'movimientos-0-debe': '100.00',
        'movimientos-0-haber': '',
        'movimientos-1-cuenta': cuenta2.pk,
        'movimientos-1-debe': '',
        'movimientos-1-haber': '100.00',
    }
    response = client.post(url, data, HTTP_HX_REQUEST='true')
    assert response.status_code == 200 # La respuesta OOB es 200
    assert AsientoContable.objects.count() == 1
    asiento = AsientoContable.objects.first()
    movimientos = MovimientoContable.objects.filter(asiento=asiento)
    assert movimientos.count() == 2
    assert sum(m.debe or 0 for m in movimientos) == 100
    assert sum(m.haber or 0 for m in movimientos) == 100

@pytest.mark.django_db
def test_crear_asiento_no_balanceado(client):
    cuenta1 = CuentaContable.objects.create(codigo='100', nombre='Caja')
    cuenta2 = CuentaContable.objects.create(codigo='200', nombre='Banco')

    url = reverse('asientos_contables:asiento_create')
    data = {
        'fecha': '2024-07-01',
        'descripcion': 'Asiento no balanceado',
        'movimientos-TOTAL_FORMS': '2',
        'movimientos-INITIAL_FORMS': '0',
        'movimientos-MIN_NUM_FORMS': '0',
        'movimientos-MAX_NUM_FORMS': '1000',
        'movimientos-0-cuenta': cuenta1.pk,
        'movimientos-0-debe': '100.00',
        'movimientos-0-haber': '',
        'movimientos-1-cuenta': cuenta2.pk,
        'movimientos-1-debe': '',
        'movimientos-1-haber': '50.00',
    }
    response = client.post(url, data, HTTP_HX_REQUEST='true')
    # Debe quedarse en la misma página y mostrar error
    assert response.status_code == 200
    assert AsientoContable.objects.count() == 0
    assert "El asiento no está balanceado" in response.content.decode()

@pytest.mark.django_db
def test_no_se_permite_movimiento_vacio(client):
    cuenta1 = CuentaContable.objects.create(codigo='100', nombre='Caja')
    url = reverse('asientos_contables:asiento_create')
    data = {
        'fecha': '2024-07-01',
        'descripcion': 'Asiento con movimiento vacío',
        'movimientos-TOTAL_FORMS': '2',
        'movimientos-INITIAL_FORMS': '0',
        'movimientos-MIN_NUM_FORMS': '0',
        'movimientos-MAX_NUM_FORMS': '1000',
        'movimientos-0-cuenta': cuenta1.pk,
        'movimientos-0-debe': '',
        'movimientos-0-haber': '',
        'movimientos-1-cuenta': cuenta1.pk,
        'movimientos-1-debe': '100.00',
        'movimientos-1-haber': '',
    }
    response = client.post(url, data, HTTP_HX_REQUEST='true')
    assert response.status_code == 200
    assert AsientoContable.objects.count() == 0
    assert "Debe ingresar un valor en debe o haber" in response.content.decode()
