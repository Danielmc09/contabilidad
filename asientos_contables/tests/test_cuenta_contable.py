from django.test import TestCase
import pytest
from django.urls import reverse
from asientos_contables.models import CuentaContable
import factory

# Create your tests here.

class CuentaContableFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CuentaContable
    codigo = factory.Sequence(lambda n: f"C{n:04d}")
    nombre = factory.Faker('word')
    descripcion = factory.Faker('sentence')

@pytest.fixture
def cuenta_factory(db):
    def make(**kwargs):
        return CuentaContableFactory(**kwargs)
    return make

@pytest.mark.django_db
def test_crear_cuenta(client):
    url = reverse('asientos_contables:cuenta_create')
    data = {'codigo': 'TEST01', 'nombre': 'Test', 'descripcion': 'Cuenta de prueba'}
    response = client.post(url, data, HTTP_HX_REQUEST='true')
    assert response.status_code == 200
    assert CuentaContable.objects.filter(codigo='TEST01').exists()

@pytest.mark.django_db
def test_no_duplicados(client, cuenta_factory):
    cuenta_factory(codigo='DUPLI')
    url = reverse('asientos_contables:cuenta_create')
    data = {'codigo': 'DUPLI', 'nombre': 'Otro', 'descripcion': ''}
    response = client.post(url, data, HTTP_HX_REQUEST='true')
    assert "Ya existe una cuenta contable con este código." in response.content.decode()

@pytest.mark.django_db
def test_editar_cuenta(client, cuenta_factory):
    cuenta = cuenta_factory(nombre='Original')
    url = reverse('asientos_contables:cuenta_update', args=[cuenta.pk])
    data = {'codigo': cuenta.codigo, 'nombre': 'Editado', 'descripcion': cuenta.descripcion}
    response = client.post(url, data, HTTP_HX_REQUEST='true')
    cuenta.refresh_from_db()
    assert cuenta.nombre == 'Editado'

@pytest.mark.django_db
def test_eliminar_cuenta(client, cuenta_factory):
    cuenta = cuenta_factory()
    url = reverse('asientos_contables:cuenta_delete', args=[cuenta.pk])
    response = client.post(url, {}, HTTP_HX_REQUEST='true')
    assert response.status_code == 200
    assert not CuentaContable.objects.filter(pk=cuenta.pk).exists()

@pytest.mark.django_db
def test_listar_cuentas(client, cuenta_factory):
    cuenta_factory(codigo='A001', nombre='Caja')
    cuenta_factory(codigo='A002', nombre='Banco')
    url = reverse('asientos_contables:cuenta_list')
    response = client.get(url)
    assert 'Caja' in response.content.decode()
    assert 'Banco' in response.content.decode()
