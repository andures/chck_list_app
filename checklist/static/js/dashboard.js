// Función para simular la API si no existe
function simulateApiResponse(listId) {
    // Obtener los elementos del DOM para esta lista
    const listCard = document.querySelector(`.modern-card[data-list-id="${listId}"]`)
    if (!listCard) return null
  
    // Contar tareas directamente del DOM como fallback
    const totalElement = listCard.querySelector(`.task-total[data-list-id="${listId}"]`)
    const todoElement = listCard.querySelector(`.task-todo[data-list-id="${listId}"]`)
    const doneElement = listCard.querySelector(`.task-done[data-list-id="${listId}"]`)
  
    const total = totalElement ? Number.parseInt(totalElement.textContent) : 0
    const todo = todoElement ? Number.parseInt(todoElement.textContent) : 0
    const done = doneElement ? Number.parseInt(doneElement.textContent) : 0
  
    return { total, todo, done }
  }
  
  // Sobrescribir el fetch para manejar la API simulada
  const originalFetch = window.fetch
  window.fetch = (url, options) => {
    if (url.startsWith("/api/todo-list/")) {
      // Extraer el ID de la lista de la URL
      const listIdMatch = url.match(/\/api\/todo-list\/(\d+)\/stats\//)
      if (listIdMatch && listIdMatch[1]) {
        const listId = listIdMatch[1]
        const response = simulateApiResponse(listId)
  
        if (response) {
          return Promise.resolve({
            json: () => Promise.resolve(response),
            ok: true,
          })
        }
      }
    }
  
    // Si no es una URL de API simulada, usar el fetch original
    return originalFetch(url, options)
  }
  
  // Función para actualizar las estadísticas cuando se cambia una tarea en otra página
  function notifyTaskStatusChanged() {
    localStorage.setItem("taskStatusChanged", Date.now().toString())
  }
  
  // Exportar la función para que pueda ser usada en otras páginas
  window.notifyTaskStatusChanged = notifyTaskStatusChanged
  
  document.addEventListener("DOMContentLoaded", () => {
    // Función para actualizar las estadísticas del dashboard
    function updateDashboardStats() {
      console.log("Actualizando estadísticas del dashboard")
  
      // Actualizar estadísticas de listas recientes
      const todoLists = document.querySelectorAll(".modern-card[data-list-id]")
      let totalCompletedTasks = 0
  
      // Si no hay listas en el dashboard, no hacer nada
      if (todoLists.length === 0) {
        return
      }
  
      // Actualizar cada lista individualmente
      todoLists.forEach((list) => {
        const listId = list.getAttribute("data-list-id")
        if (!listId) return
  
        // Hacer una petición para obtener los datos actualizados de la lista
        fetch(`/todo_list/${listId}/`, {
          method: "GET",
          headers: {
            "X-Requested-With": "XMLHttpRequest",
          },
        })
          .then((response) => {
            if (!response.ok) {
              throw new Error("Error al obtener datos de la lista")
            }
            return response.text()
          })
          .then((html) => {
            // Crear un elemento temporal para analizar el HTML
            const tempDiv = document.createElement("div")
            tempDiv.innerHTML = html
  
            // Extraer los contadores de tareas
            const todoCount = tempDiv.querySelectorAll("#todo-tasks .task-card").length
            const progressCount = tempDiv.querySelectorAll("#progress-tasks .task-card").length
            const doneCount = tempDiv.querySelectorAll("#done-tasks .task-card").length
            const totalCount = todoCount + progressCount + doneCount
  
            // Actualizar los contadores en la tarjeta
            const todoElement = list.querySelector(".stat-pill:nth-child(2) .stat-value")
            const doneElement = list.querySelector(".stat-pill:nth-child(3) .stat-value")
            const totalElement = list.querySelector(".stat-pill:nth-child(1) .stat-value")
  
            if (totalElement) totalElement.textContent = totalCount
            if (todoElement) todoElement.textContent = todoCount
            if (doneElement) doneElement.textContent = doneCount
  
            // Acumular el total de tareas completadas
            totalCompletedTasks += doneCount
  
            // Actualizar el contador global de tareas completadas
            const totalCompletedElement = document.querySelector(".modern-stat:nth-child(2) .stat-card-title")
            if (totalCompletedElement) {
              totalCompletedElement.textContent = totalCompletedTasks
            }
          })
          .catch((error) => {
            console.error("Error al actualizar lista:", error)
          })
      })
    }
  
    // Actualizar estadísticas cuando se carga la página
    updateDashboardStats()
  
    // Actualizar estadísticas cuando el usuario regresa a la página
    window.addEventListener("focus", updateDashboardStats)
  
    // Actualizar estadísticas cada 30 segundos
    setInterval(updateDashboardStats, 30000)
  
    // Escuchar cambios en localStorage (comunicación entre páginas)
    window.addEventListener("storage", (event) => {
      if (event.key === "taskStatusChanged") {
        console.log("Detectado cambio en tareas, actualizando dashboard")
        updateDashboardStats()
      }
    })
  })  