document.addEventListener('DOMContentLoaded', function() {
    // Seleccionar todos los elementos de tarjetas de tareas
    const taskCards = document.querySelectorAll('.task-card');
    const taskColumns = document.querySelectorAll('.task-items');
    const taskCounts = document.querySelectorAll('.task-count');
  
    // Hacer que cada tarjeta sea arrastrable
    taskCards.forEach(card => {
      card.setAttribute('draggable', 'true');
      card.addEventListener('dragstart', dragStart);
      card.addEventListener('dragend', dragEnd);
    });
  
    // Configurar las zonas donde se pueden soltar las tarjetas
    taskColumns.forEach(column => {
      column.addEventListener('dragover', dragOver);
      column.addEventListener('dragenter', dragEnter);
      column.addEventListener('dragleave', dragLeave);
      column.addEventListener('drop', drop);
    });
  
    // Variable para almacenar la tarjeta que se está arrastrando
    let draggedCard = null;
  
    // Función que se ejecuta cuando se comienza a arrastrar una tarjeta
    function dragStart(e) {
      draggedCard = this;
      // Agregar una clase para estilo visual durante el arrastre
      setTimeout(() => {
        this.classList.add('dragging');
      }, 0);
      
      // Almacenar datos sobre la tarjeta que se está arrastrando
      e.dataTransfer.setData('text/plain', this.innerHTML);
      e.dataTransfer.effectAllowed = 'move';
    }
  
    // Función que se ejecuta cuando se termina de arrastrar
    function dragEnd() {
      this.classList.remove('dragging');
      // Actualizar los contadores de tareas
      updateTaskCounts();
    }
  
    // Permitir que la zona acepte elementos arrastrados
    function dragOver(e) {
      e.preventDefault();
      return false;
    }
  
    // Función que se ejecuta cuando un elemento arrastrado entra en la zona
    function dragEnter(e) {
      e.preventDefault();
      this.classList.add('drag-over');
    }
  
    // Función que se ejecuta cuando un elemento arrastrado sale de la zona
    function dragLeave() {
      this.classList.remove('drag-over');
    }
  
    // Función que se ejecuta cuando se suelta un elemento en la zona
    function drop(e) {
      e.preventDefault();
      
      // Remover la clase de estilo de la zona
      this.classList.remove('drag-over');
      
      // Solo permitir soltar si estamos arrastrando una tarjeta y la soltamos en una columna diferente
      if (draggedCard && this !== draggedCard.parentNode) {
        // Remover la tarjeta de su posición original
        draggedCard.parentNode.removeChild(draggedCard);
        
        // Agregar la tarjeta a la nueva columna
        this.appendChild(draggedCard);
        
        // Efecto visual para la nueva tarjeta
        draggedCard.classList.add('just-dropped');
        setTimeout(() => {
          draggedCard.classList.remove('just-dropped');
        }, 500);
      }
      
      return false;
    }
  
    // Función para actualizar los contadores de tareas en cada columna
    function updateTaskCounts() {
      const columns = document.querySelectorAll('.task-column');
      
      columns.forEach((column, index) => {
        const count = column.querySelector('.task-items').children.length;
        const countElement = column.querySelector('.task-count');
        countElement.textContent = count;
      });
    }
  
    // Inicializar los contadores de tareas
    updateTaskCounts();
  });