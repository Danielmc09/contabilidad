# Sistema de Contabilidad con Django y HTMX

Este proyecto es una aplicación de contabilidad desarrollada en Django que permite la gestión de Cuentas Contables y Asientos Contables. Fue construido como parte de una prueba técnica, con un enfoque en la calidad del código, la arquitectura sostenible y las mejores prácticas de desarrollo.

## Resumen de la Arquitectura y Decisiones de Diseño

Más allá de cumplir con los requisitos básicos, se tomaron decisiones de arquitectura para asegurar que el proyecto sea mantenible, escalable y eficiente, siguiendo principios de diseño como **SOLID** y **DRY**.

*   **Modelos Optimizados:**
    *   **Manager Personalizado:** El modelo `AsientoContable` utiliza un `Manager` de Django personalizado (`AsientoContableManager`) con el método `with_totals()`. Este método aprovecha `annotate()` para calcular los totales de "Debe" y "Haber" a nivel de base de datos, previniendo el conocido problema de rendimiento "N+1" al listar asientos.
    *   **Validación Encapsulada:** La lógica de negocio para validar que un asiento esté balanceado (Debe == Haber) se ha encapsulado en un `BaseInlineFormSet` personalizado, separando las responsabilidades de la vista y adhiriéndose al principio de "Fat Models, Thin Views" (y "Smart Forms").

*   **Vistas y Lógica Reutilizable (DRY):**
    *   **Mixins para HTMX:** Se crearon dos `Mixins` principales (`HtmxListViewMixin` y `HtmxFormMixin`) para abstraer toda la lógica repetitiva relacionada con las peticiones HTMX. Esto incluye el manejo de respuestas para modales, actualización de tablas parciales y el envío de eventos al frontend.
    *   **Vistas Declarativas:** Como resultado, las Vistas Basadas en Clases (CBV) son extremadamente limpias y declarativas. Simplemente heredan de los mixins y definen atributos, haciendo que el código sea fácil de leer y extender.

*   **Comunicación Frontend-Backend Desacoplada:**
    *   **Eventos vía Headers:** La interacción se maneja a través de headers de respuesta HTMX (`HX-Trigger`) en formato JSON. El backend notifica eventos como `closeModal` o `showMessage`, y el frontend escucha y reacciona. Esto desacopla completamente el backend (lógica de negocio) del frontend (manipulación del DOM).

*   **Entorno de Desarrollo Profesional:**
    *   **Gestión Centralizada:** Se utiliza `pyproject.toml` con `uv` para gestionar todas las dependencias del proyecto y de desarrollo, así como la configuración de herramientas de calidad de código como `black`, `isort` y `pytest`.
    *   **Seguridad y Configuración:** El proyecto está configurado para leer información sensible (como `SECRET_KEY` y credenciales de la base de datos) desde variables de entorno, utilizando un archivo `.env` que no se versiona, siguiendo las mejores prácticas de seguridad.

## Tech Stack

*   **Backend:** Django, Django-HTMX
*   **Frontend:** HTMX, Bootstrap
*   **Base de Datos:** PostgreSQL
*   **Testing:** Pytest, Pytest-Django, Factory-Boy
*   **Contenerización:** Docker, Docker Compose
*   **Gestión de Dependencias:** uv

---

## Instrucciones de Configuración y Ejecución

### Prerrequisitos

*   Docker y Docker Compose
*   Tener un archivo `.env` en la raíz del proyecto. Puede crearlo a partir del archivo de ejemplo:
    ```bash
    cp .env.example .env
    ```

### Ejecución con Docker

El proyecto está completamente dockerizado para una fácil configuración.

1.  **Construir y levantar los contenedores:**
    Desde la raíz del proyecto, ejecute:
    ```bash
    docker-compose up --build -d
    ```
    El flag `-d` inicia los contenedores en segundo plano.

2.  **Acceder a la aplicación:**
    La aplicación estará disponible en `http://localhost:8000`.

3.  **Crear un Superusuario (Opcional):**
    Para acceder al panel de administración de Django, puede crear un superusuario:
    ```bash
    docker-compose exec web python manage.py createsuperuser
    ```
    El panel de admin está en `http://localhost:8000/admin`.

### Ejecución de Pruebas

Las pruebas unitarias están implementadas con Pytest. Para ejecutarlas, utilice el siguiente comando:

```bash
docker-compose exec web pytest
```

---

## Estructura del Proyecto

```
contabilidad/
├── asientos_contables/  # App principal de Django
│   ├── migrations/
│   ├── static/
│   ├── templates/
│   ├── tests/           # Pruebas unitarias
│   ├── __init__.py
│   ├── models.py        # Modelos optimizados
│   ├── forms.py         # Formularios y Formsets con lógica de validación
│   ├── views.py         # Vistas limpias y basadas en Mixins
│   └── urls.py
├── contabilidad/        # Configuración del proyecto Django
│   ├── settings.py      # Configuración segura con variables de entorno
│   └── urls.py
├── .env.example         # Plantilla de variables de entorno
├── docker-compose.yml   # Orquestación de contenedores
├── Dockerfile           # Definición del contenedor de la aplicación
├── pyproject.toml       # Gestión de dependencias y herramientas
└── README.md
```

---

## 🚀 Características principales
- **CRUD completo de cuentas contables** con búsqueda en tiempo real y modales (HTMX).
- **Gestión de asientos contables**: listado profesional, creación con movimientos dinámicos (agregar/quitar filas antes de guardar).
- **Validación visual y backend**: balanceo en tiempo real y al guardar.
- **UX/UI moderna**: Bootstrap 5, Bootstrap Icons, responsive, accesible.
- **Pruebas unitarias**: cobertura de los flujos principales de negocio.
- **Docker y docker-compose**: despliegue y pruebas fáciles en cualquier entorno.

---

## 🧩 Modelos y lógica de negocio

- **CuentaContable**: código, nombre, descripción. CRUD completo, búsqueda, validación de unicidad.
- **AsientoContable**: fecha, descripción, métodos de balanceo y totales, agrupa movimientos.
- **MovimientoContable**: cuenta (FK), debe, haber, asiento (FK). Validación: solo uno de debe/haber, nunca ambos ni ninguno.
- **Validaciones clave**: no se puede guardar un asiento si la suma de debe ≠ haber; no se permite movimiento vacío.

---

## 🖥️ Vistas y plantillas

- **CRUD de cuentas**: listado, creación, edición, eliminación, búsqueda en tiempo real, modales con HTMX.
- **Asientos**: listado profesional, creación con movimientos dinámicos (agregar/quitar filas), validación visual y backend, mensajes claros.
- **Movimientos**: agregar/quitar antes de guardar, validación visual y backend, UX moderna.
- **Detalle de asiento**: modal con todos los movimientos y totales.

---

## 🌐 URLs
- Namespacing correcto (`asientos_contables:`).
- Rutas para CRUD de cuentas y asientos.
- Endpoints parciales para HTMX.

---

## 🧪 Pruebas unitarias

- **Cobertura:**
  - CRUD de cuentas: crear, editar, eliminar, no duplicados, listar.
  - Asientos: creación balanceada, error si no balanceado, error si movimiento vacío.
- **Framework:** pytest + pytest-django.
- **Ejecución:**
  ```bash
  pytest
  ```
- **Ejemplo de salida:**
  ```
  asientos_contables/tests/test_asiento_contable.py::test_crear_asiento_balanceado PASSED
  asientos_contables/tests/test_asiento_contable.py::test_crear_asiento_no_balanceado PASSED
  asientos_contables/tests/test_asiento_contable.py::test_no_se_permite_movimiento_vacio PASSED
  asientos_contables/tests/test_cuenta_contable.py::test_crear_cuenta PASSED
  ...
  ```

---

## 🎯 Uso y flujos principales

- **Cuentas contables**: CRUD completo, búsqueda en tiempo real, modales, validación de unicidad.
- **Asientos contables**: listado profesional, creación con movimientos dinámicos, validación visual y backend, mensajes claros.
- **Movimientos**: agregar/quitar antes de guardar, validación visual y backend.
- **Validación visual**: balanceo en tiempo real, mensajes de error y éxito.
- **Detalle de asiento**: modal con todos los movimientos y totales.

---

## 🛠️ Solución de problemas

- **Modal no se cierra**: revisa fragmentos OOB y función `closeModal()`.
- **Validación no funciona**: revisa que los listeners JS se asignen tras agregar filas.
- **Pruebas no corren**: asegúrate de tener pytest y pytest-django instalados.

---

## 📄 Licencia y contribución

- Licencia MIT.
- Pull requests y sugerencias bienvenidas.

---

## ✅ Checklist de entrega
- [x] CRUD de cuentas (con HTMX)
- [x] Listado y creación de asientos con movimientos dinámicos
- [x] Validación visual y backend
- [x] Pruebas unitarias cubriendo los flujos principales
- [x] Docker y docker-compose funcionales
- [x] README claro y completo
- [x] Código limpio y sin prints innecesarios

---

¿Dudas o sugerencias? Abre un issue en el repo.
