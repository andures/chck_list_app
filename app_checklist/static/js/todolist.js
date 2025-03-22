document.addEventListener('DOMContentLoaded', function() {
    // Variables globales
    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || 
                      document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1];
    const todoTasks = document.getElementById('todo-tasks');
    const progressTasks = document.getElementById('progress-tasks');
    const doneTasks = document.getElementById('done-tasks');
    const deleteTaskModalElement = document.getElementById('deleteTaskModal');
    const deleteTaskModal = new bootstrap.Modal(deleteTaskModalElement);
    const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
    const toastContainer = document.getElementById('toastContainer');
    
    let currentTaskId = null;
    
    // Configurar eventos de arrastrar y soltar
    setupDragAndDrop();
    
    // Configurar eventos de botones
    setupEventListeners();
    
    // Función para configurar eventos de arrastrar y soltar
    function setupDragAndDrop() {
      // Hacer que las tareas sean arrastrables
      const taskCards = document.querySelectorAll('.task-card');
      taskCards.forEach(card => {
        card.addEventListener('dragstart', handleDragStart);
        card.addEventListener('dragend', handleDragEnd);
      });
      
      // Configurar contenedores de tareas para recibir elementos arrastrados
      const taskContainers = document.querySelectorAll('.task-items');
      taskContainers.forEach(container => {
        container.addEventListener('dragover', handleDragOver);
        container.addEventListener('dragenter', handleDragEnter);
        container.addEventListener('dragleave', handleDragLeave);
        container.addEventListener('drop', handleDrop);
      });
    }
    
    // Función para manejar el inicio del arrastre
    function handleDragStart(e) {
      e.dataTransfer.setData('text/plain', this.id);
      e.dataTransfer.effectAllowed = 'move';
      this.classList.add('dragging');
    }
    
    // Función para manejar el fin del arrastre
    function handleDragEnd() {
      this.classList.remove('dragging');
    }
    
    // Función para manejar el evento dragover
    function handleDragOver(e) {
      e.preventDefault();
      return false;
    }
    
    // Función para manejar el evento dragenter
    function handleDragEnter(e) {
      e.preventDefault();
      this.classList.add('drag-over');
    }
    
    // Función para manejar el evento dragleave
    function handleDragLeave() {
      this.classList.remove('drag-over');
    }
    
    // Función para manejar el evento drop
    function handleDrop(e) {
      e.preventDefault();
      this.classList.remove('drag-over');
      
      const taskId = e.dataTransfer.getData('text/plain').replace('task-', '');
      const newStatus = this.dataset.column;
      const taskCard = document.getElementById(`task-${taskId}`);
      
      if (taskCard) {
        // Mover la tarea visualmente
        this.appendChild(taskCard);
        
        // Actualizar el estado de la tarea en el servidor
        updateTaskStatus(taskId, newStatus);
        
        // Actualizar contadores
        updateTaskCounts();
        
        // Actualizar el orden de las tareas
        updateTasksOrder();
      }
      
      return false;
    }
    
    // Función para actualizar el estado de una tarea
    function updateTaskStatus(taskId, newStatus) {
      fetch(`/api/tasks/${taskId}/status/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
          status: newStatus
        })
      })
      .then(response => {
        if (!response.ok) {
          throw new Error('Error al actualizar el estado de la tarea');
        }
        return response.json();
      })
      .then(data => {
        showToast('Estado de la tarea actualizado correctamente', 'success');
      })
      .catch(error => {
        console.error('Error:', error);
        showToast(error.message, 'error');
      });
    }
    
    // Función para actualizar el orden de las tareas
    function updateTasksOrder() {
      // Obtener el ID de la lista de la URL
      const pathParts = window.location.pathname.split('/');
      const listId = pathParts[pathParts.indexOf('lists') + 1];
      
      // Obtener el orden actual de las tareas
      const taskOrder = {
        todo: Array.from(todoTasks.querySelectorAll('.task-card')).map(card => card.dataset.taskId),
        progress: Array.from(progressTasks.querySelectorAll('.task-card')).map(card => card.dataset.taskId),
        done: Array.from(doneTasks.querySelectorAll('.task-card')).map(card => card.dataset.taskId)
      };
      
      // Enviar el orden al servidor
      fetch(`/api/lists/${listId}/order/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken
        },
        body: JSON.stringify(taskOrder)
      })
      .then(response => {
        if (!response.ok) {
          throw new Error('Error al actualizar el orden de las tareas');
        }
        return response.json();
      })
      .catch(error => {
        console.error('Error:', error);
        showToast(error.message, 'error');
      });
    }
    
    // Función para actualizar los contadores de tareas
    function updateTaskCounts() {
      const todoCount = todoTasks.querySelectorAll('.task-card').length;
      const progressCount = progressTasks.querySelectorAll('.task-card').length;
      const doneCount = doneTasks.querySelectorAll('.task-card').length;
      
      document.querySelector('.task-column:nth-child(1) .task-count').textContent = todoCount;
      document.querySelector('.task-column:nth-child(2) .task-count').textContent = progressCount;
      document.querySelector('.task-column:nth-child(3) .task-count').textContent = doneCount;
    }
    
    // Función para eliminar una tarea
    function deleteTask(taskId) {
      fetch(`/tasks/${taskId}/delete/`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrfToken,
          'Content-Type': 'application/json'
        }
      })
      .then(response => {
        if (!response.ok) {
          throw new Error('Error al eliminar la tarea');
        }
        
        // Eliminar la tarea del DOM
        const taskCard = document.getElementById(`task-${taskId}`);
        if (taskCard) {
          taskCard.remove();
          
          // Actualizar contadores
          updateTaskCounts();
          
          // Mostrar mensaje de éxito
          showToast('Tarea eliminada correctamente', 'success');
        }
      })
      .catch(error => {
        console.error('Error:', error);
        showToast(error.message, 'error');
      });
    }
    
    // Configurar eventos de botones
    function setupEventListeners() {
      // Botones para eliminar tareas
      document.querySelectorAll('.delete-btn').forEach(btn => {
        btn.addEventListener('click', function() {
          currentTaskId = this.dataset.taskId;
        });
      });
      
      // Botón de confirmación para eliminar tarea
      confirmDeleteBtn.addEventListener('click', function() {
        if (currentTaskId) {
          deleteTask(currentTaskId);
          deleteTaskModal.hide();
        }
      });
    }
    
    // Función para mostrar notificaciones
    function showToast(message, type = 'info') {
      const toast = document.createElement('div');
      toast.className = `toast toast-${type} show`;
      toast.setAttribute('role', 'alert');
      toast.setAttribute('aria-live', 'assertive');
      toast.setAttribute('aria-atomic', 'true');
      
      toast.innerHTML = `
        <div class="toast-body">
          ${message}
        </div>
      `;
      
      toastContainer.appendChild(toast);
      
      // Eliminar después de 3 segundos
      setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
          toastContainer.removeChild(toast);
        }, 300);
      }, 3000);
    }
  });