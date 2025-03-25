import Sortable from "sortablejs"
import * as bootstrap from "bootstrap"

document.addEventListener("DOMContentLoaded", () => {
  // Mostrar/ocultar opciones de escala según el tipo de pregunta
  const questionTypeSelect = document.getElementById("id_question_type")
  const linearScaleFields = document.getElementById("linearScaleFields")

  if (questionTypeSelect) {
    questionTypeSelect.addEventListener("change", function () {
      if (this.value === "linear_scale") {
        linearScaleFields.classList.remove("d-none")
        updateScalePreview()
      } else {
        linearScaleFields.classList.add("d-none")
      }
    })
  }

  // Inicializar Sortable para las preguntas
  const questionsContainer = document.getElementById("questionsList")
  if (questionsContainer) {
    new Sortable(questionsContainer, {
      animation: 150,
      handle: ".card-header",
      ghostClass: "sortable-ghost",
      onEnd: () => {
        updateQuestionsOrder()
      },
    })
  }

  // Inicializar Sortable para las opciones
  document.querySelectorAll(".options-list").forEach((el) => {
    new Sortable(el, {
      animation: 150,
      handle: ".option-handle",
      ghostClass: "sortable-ghost",
      onEnd: () => {
        const questionId = el.dataset.questionId
        updateOptionsOrder(questionId)
      },
    })
  })

  // Actualizar orden de preguntas
  function updateQuestionsOrder() {
    const questionIds = Array.from(document.querySelectorAll(".question-card")).map((el) => el.dataset.id)
    const formId = document.getElementById("form-id")?.value || window.location.pathname.split("/")[2]

    fetch(`/forms/${formId}/update-question-order/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
      },
      body: JSON.stringify({ question_ids: questionIds }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (!data.success) {
          console.error("Error al actualizar el orden de las preguntas:", data.error)
        }
      })
      .catch((error) => {
        console.error("Error:", error)
      })
  }

  // Actualizar orden de opciones
  function updateOptionsOrder(questionId) {
    const optionsList = document.querySelector(`.options-list[data-question-id="${questionId}"]`)
    const optionIds = Array.from(optionsList.querySelectorAll(".option-item")).map((el) => el.dataset.id)

    fetch(`/forms/question/${questionId}/update-option-order/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
      },
      body: JSON.stringify({ option_ids: optionIds }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (!data.success) {
          console.error("Error al actualizar el orden de las opciones:", data.error)
        }
      })
      .catch((error) => {
        console.error("Error:", error)
      })
  }

  // Mostrar formulario de pregunta
  const addQuestionBtn = document.getElementById("add-question-btn")
  if (addQuestionBtn) {
    addQuestionBtn.addEventListener("click", () => {
      // Obtener el formulario de añadir pregunta
      const addQuestionForm = document.getElementById("question-form")

      // Hacer scroll hasta el formulario
      if (addQuestionForm) {
        addQuestionForm.scrollIntoView({ behavior: "smooth" })

        // Enfocar el primer campo del formulario
        const firstInput = addQuestionForm.querySelector("input, select, textarea")
        if (firstInput) {
          setTimeout(() => {
            firstInput.focus()
          }, 500) // Pequeño retraso para asegurar que el scroll ha terminado
        }
      }
    })
  }

  // Editar pregunta
  document.querySelectorAll(".edit-question").forEach((button) => {
    button.addEventListener("click", function () {
      const questionId = this.dataset.questionId
      const questionCard = document.querySelector(`.question-card[data-question-id="${questionId}"]`)

      // Obtener datos de la pregunta
      const questionText = questionCard.querySelector(".card-title").textContent
      const questionType = questionCard.querySelector(".question-type-badge").textContent
      const helpText = questionCard.querySelector(".text-muted.small")?.textContent || ""
      const isRequired = questionCard.querySelector(".required-badge") !== null

      // Llenar el formulario de edición
      document.getElementById("edit-question-text").value = questionText

      // Seleccionar el tipo de pregunta correcto
      const typeSelect = document.getElementById("edit-question-type")
      for (let i = 0; i < typeSelect.options.length; i++) {
        if (typeSelect.options[i].text === questionType) {
          typeSelect.selectedIndex = i
          break
        }
      }

      document.getElementById("edit-question-help-text").value = helpText
      document.getElementById("edit-question-required").checked = isRequired

      // Mostrar/ocultar opciones de escala
      const editScaleOptions = document.getElementById("edit-scale-options")
      if (typeSelect.value === "linear_scale") {
        editScaleOptions.classList.remove("d-none")

        // Obtener valores de escala si existen
        const minValue = questionCard.querySelector('[name="min_value"]')?.value || 1
        const maxValue = questionCard.querySelector('[name="max_value"]')?.value || 5
        const minLabel = questionCard.querySelector(".scale-labels")?.firstElementChild.textContent || ""
        const maxLabel = questionCard.querySelector(".scale-labels")?.lastElementChild.textContent || ""

        document.getElementById("edit-min-value").value = minValue
        document.getElementById("edit-max-value").value = maxValue
        document.getElementById("edit-min-label").value = minLabel
        document.getElementById("edit-max-label").value = maxLabel
      } else {
        editScaleOptions.classList.add("d-none")
      }

      // Mostrar imagen actual si existe
      const imageContainer = document.getElementById("current-image-container")
      const currentImage = document.getElementById("current-image")
      const questionImage = questionCard.querySelector("img")

      if (questionImage) {
        currentImage.src = questionImage.src
        imageContainer.classList.remove("d-none")
      } else {
        imageContainer.classList.add("d-none")
      }

      // Configurar el formulario para enviar a la URL correcta
      const editForm = document.getElementById("edit-question-form")
      editForm.action = `/forms/question/${questionId}/edit/`

      // Mostrar el modal
      const modal = new bootstrap.Modal(document.getElementById("editQuestionModal"))
      modal.show()

      // Configurar el botón de guardar
      document.getElementById("save-question-btn").onclick = () => {
        editForm.submit()
      }

      // Actualizar opciones de escala al cambiar el tipo
      document.getElementById("edit-question-type").addEventListener("change", function () {
        if (this.value === "linear_scale") {
          editScaleOptions.classList.remove("d-none")
        } else {
          editScaleOptions.classList.add("d-none")
        }
      })
    })
  })

  // Eliminar pregunta
  document.querySelectorAll(".delete-question").forEach((button) => {
    button.addEventListener("click", function () {
      const questionId = this.dataset.questionId
      const questionText = document.querySelector(
        `.question-card[data-question-id="${questionId}"] .card-title`,
      ).textContent

      document.getElementById("delete-confirm-message").textContent =
        `¿Estás seguro de que deseas eliminar la pregunta "${questionText}"?`

      const modal = new bootstrap.Modal(document.getElementById("deleteConfirmModal"))
      modal.show()

      document.getElementById("confirm-delete-btn").onclick = () => {
        fetch(`/forms/question/${questionId}/delete/`, {
          method: "POST",
          headers: {
            "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
            "X-Requested-With": "XMLHttpRequest",
          },
        })
          .then((response) => response.json())
          .then((data) => {
            if (data.success) {
              document.querySelector(`.question-card[data-question-id="${questionId}"]`).remove()
              modal.hide()
            } else {
              console.error("Error al eliminar la pregunta")
            }
          })
          .catch((error) => {
            console.error("Error:", error)
          })
      }
    })
  })

  // Añadir opción
  document.querySelectorAll(".add-option").forEach((button) => {
    button.addEventListener("click", function () {
      const questionId = this.dataset.questionId

      // Configurar el formulario
      const optionForm = document.getElementById("option-form")
      optionForm.action = `/forms/question/${questionId}/add-option/`
      document.getElementById("option-text").value = ""

      // Actualizar título del modal
      document.getElementById("optionModalLabel").textContent = "Añadir Opción"

      // Mostrar el modal
      const modal = new bootstrap.Modal(document.getElementById("optionModal"))
      modal.show()

      // Configurar el botón de guardar
      document.getElementById("save-option-btn").onclick = () => {
        optionForm.submit()
      }
    })
  })

  // Editar opción
  document.querySelectorAll(".edit-option").forEach((button) => {
    button.addEventListener("click", function () {
      const optionId = this.dataset.optionId
      const optionText = this.parentElement.previousElementSibling.textContent

      // Configurar el formulario
      const optionForm = document.getElementById("option-form")
      optionForm.action = `/forms/option/${optionId}/edit/`
      document.getElementById("option-text").value = optionText

      // Actualizar título del modal
      document.getElementById("optionModalLabel").textContent = "Editar Opción"

      // Mostrar el modal
      const modal = new bootstrap.Modal(document.getElementById("optionModal"))
      modal.show()

      // Configurar el botón de guardar
      document.getElementById("save-option-btn").onclick = () => {
        optionForm.submit()
      }
    })
  })

  // Eliminar opción
  document.querySelectorAll(".delete-option").forEach((button) => {
    button.addEventListener("click", function () {
      const optionId = this.dataset.optionId
      const optionText = this.parentElement.previousElementSibling.textContent

      document.getElementById("delete-confirm-message").textContent =
        `¿Estás seguro de que deseas eliminar la opción "${optionText}"?`

      const modal = new bootstrap.Modal(document.getElementById("deleteConfirmModal"))
      modal.show()

      document.getElementById("confirm-delete-btn").onclick = () => {
        fetch(`/forms/option/${optionId}/delete/`, {
          method: "POST",
          headers: {
            "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
            "X-Requested-With": "XMLHttpRequest",
          },
        })
          .then((response) => response.json())
          .then((data) => {
            if (data.success) {
              document.querySelector(`.option-item[data-option-id="${optionId}"]`).remove()
              modal.hide()
            } else {
              console.error("Error al eliminar la opción")
            }
          })
          .catch((error) => {
            console.error("Error:", error)
          })
      }
    })
  })

  // Actualizar vista previa de escala lineal
  const minValueInput = document.getElementById("id_min_value")
  const maxValueInput = document.getElementById("id_max_value")
  const minLabelInput = document.getElementById("id_min_label")
  const maxLabelInput = document.getElementById("id_max_label")
  const previewMinLabel = document.getElementById("preview-min-label")
  const previewMaxLabel = document.getElementById("preview-max-label")
  const scalePreviewOptions = document.querySelector(".scale-preview-options")

  function updateScalePreview() {
    if (minValueInput && maxValueInput && scalePreviewOptions) {
      const minVal = Number.parseInt(minValueInput.value) || 1
      const maxVal = Number.parseInt(maxValueInput.value) || 5

      // Actualizar etiquetas
      if (previewMinLabel && minLabelInput) {
        previewMinLabel.textContent = minLabelInput.value || "Muy insatisfecho"
      }

      if (previewMaxLabel && maxLabelInput) {
        previewMaxLabel.textContent = maxLabelInput.value || "Muy satisfecho"
      }

      // Actualizar opciones
      if (scalePreviewOptions) {
        scalePreviewOptions.innerHTML = ""
        for (let i = minVal; i <= maxVal; i++) {
          const span = document.createElement("span")
          span.textContent = i
          scalePreviewOptions.appendChild(span)
        }
      }
    }
  }

  // Función para actualizar la vista previa en el modal de edición
  function updateEditScalePreview() {
    const editMinValue = document.getElementById("edit_min_value")
    const editMaxValue = document.getElementById("edit_max_value")
    const editMinLabel = document.getElementById("edit_min_label")
    const editMaxLabel = document.getElementById("edit_max_label")
    const editPreviewMinLabel = document.querySelector("#editLinearScaleFields .scale-preview-labels span:first-child")
    const editPreviewMaxLabel = document.querySelector("#editLinearScaleFields .scale-preview-labels span:last-child")
    const editScalePreviewOptions = document.querySelector("#editLinearScaleFields .scale-preview-options")

    if (editMinValue && editMaxValue && editScalePreviewOptions) {
      const minVal = Number.parseInt(editMinValue.value) || 1
      const maxVal = Number.parseInt(editMaxValue.value) || 5

      // Actualizar etiquetas
      if (editPreviewMinLabel && editMinLabel) {
        editPreviewMinLabel.textContent = editMinLabel.value || "Muy insatisfecho"
      }

      if (editPreviewMaxLabel && editMaxLabel) {
        editPreviewMaxLabel.textContent = editMaxLabel.value || "Muy satisfecho"
      }

      // Actualizar opciones
      if (editScalePreviewOptions) {
        editScalePreviewOptions.innerHTML = ""
        for (let i = minVal; i <= maxVal; i++) {
          const span = document.createElement("span")
          span.textContent = i
          editScalePreviewOptions.appendChild(span)
        }
      }
    }
  }

  // Añadir event listeners para actualizar la vista previa
  if (minValueInput) minValueInput.addEventListener("input", updateScalePreview)
  if (maxValueInput) maxValueInput.addEventListener("input", updateScalePreview)
  if (minLabelInput) minLabelInput.addEventListener("input", updateScalePreview)
  if (maxLabelInput) maxLabelInput.addEventListener("input", updateScalePreview)

  // Event listeners para la vista previa en el modal de edición
  const editMinValue = document.getElementById("edit_min_value")
  const editMaxValue = document.getElementById("edit_max_value")
  const editMinLabel = document.getElementById("edit_min_label")
  const editMaxLabel = document.getElementById("edit_max_label")

  if (editMinValue) editMinValue.addEventListener("input", updateEditScalePreview)
  if (editMaxValue) editMaxValue.addEventListener("input", updateEditScalePreview)
  if (editMinLabel) editMinLabel.addEventListener("input", updateEditScalePreview)
  if (editMaxLabel) editMaxLabel.addEventListener("input", updateEditScalePreview)

  // Inicializar vistas previas
  document.addEventListener("DOMContentLoaded", () => {
    // Llamar a updateScalePreview después de que el DOM esté completamente cargado
    setTimeout(updateScalePreview, 500)
    setTimeout(updateEditScalePreview, 500)
  })
})