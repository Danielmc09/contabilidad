// === JS migrado desde base.html ===
// Variables globales para el estado del modal
let modalOpen = false;

// Cierra modal si se hace clic fuera de él
document.addEventListener('click', function (e) {
  if (e.target.id === 'modal-wrapper') {
    closeModal();
  }
});

// Maneja eventos HTMX
document.body.addEventListener('htmx:afterSwap', (e) => {
  // Si se actualizó la lista de cuentas, cerrar modal
  if (e.detail.target.id === 'cuentas-list') {
    closeModal();
  }
});

// Maneja errores HTMX
document.body.addEventListener('htmx:responseError', (e) => {
  console.error('Error en petición HTMX:', e.detail);
  alert('Error en la operación. Por favor, inténtalo de nuevo.');
});

// Abre el modal
function openModal() {
  document.getElementById('modal-wrapper').style.display = 'flex';
  setTimeout(() => {
    // Busca el primer input visible y enfócalo
    const modal = document.getElementById('modal-body');
    if (modal) {
      const input = modal.querySelector('input, textarea, select');
      if (input) input.focus();
    }
  }, 100);
}

// Cierra el modal
function closeModal() {
  document.getElementById('modal-wrapper').style.display = 'none';
  setTimeout(() => {
    document.getElementById('modal-body').innerHTML = '';
  }, 300);
}

// Cierra modal con Escape
document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape' && modalOpen) {
    closeModal();
  }
});
  
// marcar todas las peticiones como HTMX
document.body.addEventListener("htmx:configRequest", evt => {
  evt.detail.headers["HX-Request"] = "true";
});
  