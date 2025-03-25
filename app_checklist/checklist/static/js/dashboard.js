// Esperar a que el DOM esté completamente cargado
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips de Bootstrap si los usas
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
  
    // Animación para las tarjetas al cargar la página
    const cards = document.querySelectorAll('.modern-card');
    cards.forEach((card, index) => {
        setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 100 * index);
    });
  
    // Añadir efecto de hover a las tarjetas de estadísticas
    const statCards = document.querySelectorAll('.modern-stat');
    statCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.querySelector('.stat-card-title').style.color = '#6366f1';
        });
        
        card.addEventListener('mouseleave', function() {
            this.querySelector('.stat-card-title').style.color = '';
        });
    });
  
    // Añadir efecto de click a los botones de acción
    const actionButtons = document.querySelectorAll('.modern-card-actions .btn');
    actionButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            // Añadir efecto de onda al hacer clic
            const ripple = document.createElement('span');
            ripple.classList.add('ripple-effect');
            this.appendChild(ripple);
            
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            
            ripple.style.width = ripple.style.height = `${size}px`;
            ripple.style.left = `${e.clientX - rect.left - size/2}px`;
            ripple.style.top = `${e.clientY - rect.top - size/2}px`;
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
  });
  
  // Añadir CSS para el efecto de onda en los botones
  const style = document.createElement('style');
  style.textContent = `
  .ripple-effect {
    position: absolute;
    border-radius: 50%;
    background-color: rgba(255, 255, 255, 0.4);
    transform: scale(0);
    animation: ripple 0.6s linear;
    pointer-events: none;
  }
  
  @keyframes ripple {
    to {
        transform: scale(4);
        opacity: 0;
    }
  }
  
  .modern-card {
    opacity: 0;
    transform: translateY(20px);
    transition: opacity 0.5s ease, transform 0.5s ease;
  }
  `;
  document.head.appendChild(style);