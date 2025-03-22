document
  .getElementById("dark-mode-toggle")
  .addEventListener("click", function () {
    // Obtener el tema actual
    const currentTheme = document.documentElement.getAttribute("data-bs-theme");
    const newTheme = currentTheme === "light" ? "dark" : "light";

    // Cambiar el tema
    document.documentElement.setAttribute("data-bs-theme", newTheme);

    // Guardar el tema en localStorage
    localStorage.setItem("theme", newTheme);

    // Cambiar el ícono dependiendo del tema
    const icon = document.getElementById("toggle-icon");
    if (newTheme === "dark") {
      icon.classList.remove("bi-moon-fill");
      icon.classList.add("bi-sun-fill");
    } else {
      icon.classList.remove("bi-sun-fill");
      icon.classList.add("bi-moon-fill");
    }

    // Activar la animación de rotación en el ícono
    icon.classList.add("rotate-animation");

    // Eliminar la animación después de que termine
    setTimeout(() => {
      icon.classList.remove("rotate-animation");
    }, 500); // Duración de la animación: 500ms
  });

// Restaurar el tema al cargar la página
window.addEventListener("load", () => {
  const savedTheme = localStorage.getItem("theme"); // Obtener el tema guardado
  if (savedTheme) {
    // Aplicar el tema guardado
    document.documentElement.setAttribute("data-bs-theme", savedTheme);

    // Cambiar el ícono dependiendo del tema
    const icon = document.getElementById("toggle-icon");
    if (savedTheme === "dark") {
      icon.classList.remove("bi-moon-fill");
      icon.classList.add("bi-sun-fill");
    } else {
      icon.classList.remove("bi-sun-fill");
      icon.classList.add("bi-moon-fill");
    }
  }
});