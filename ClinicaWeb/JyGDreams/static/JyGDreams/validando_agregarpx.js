function calcularEdad(fechaNacimiento, hoy = new Date()) {
  const nacimiento = new Date(fechaNacimiento);
  let edad = hoy.getFullYear() - nacimiento.getFullYear();
  const mes = hoy.getMonth() - nacimiento.getMonth();

  if (mes < 0 || (mes === 0 && hoy.getDate() < nacimiento.getDate())) {
    edad--;
  }

  return edad;
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = { calcularEdad };
}

function iniciarValidacionPaciente() {
  const contenedor =
    document.getElementById("formAgregarPaciente") ||
    document.querySelector(".form-container");

  if (!contenedor || contenedor.dataset.validacionIniciada === "true") return;

  const nombreInput = contenedor.querySelector("input[name='nombre']");
  const apellidoInput = contenedor.querySelector("input[name='apellido']");
  const ocupacionInput = contenedor.querySelector("input[name='ocupacion']");
  const telefonoInput = contenedor.querySelector("input[name='telefono']");
  const fechaInput = contenedor.querySelector("input[name='fecha_nacimiento']");
  const form = contenedor.querySelector("form");

  const soloLetrasYEspacios = /[^A-Za-zÁÉÍÓÚáéíóúÑñ\s]/g;
  const soloNumeros = /\D/g;

  function tieneCaracteresInvalidosLetras(valor) {
    return /[^A-Za-zÁÉÍÓÚáéíóúÑñ\s]/.test(valor);
  }

  function tieneCaracteresInvalidosNumeros(valor) {
    return /\D/.test(valor);
  }

  function mostrarAlerta(opciones) {
    if (typeof Swal !== "undefined") {
      Swal.fire(opciones);
    } else {
      alert(opciones.text || opciones.title || "Validación");
    }
  }

  function normalizarCampoLetras(input, campoNombre) {
    if (!input) return;
    input.addEventListener("input", function () {
      const originalValue = this.value;
      if (tieneCaracteresInvalidosLetras(originalValue)) {
        mostrarAlerta({
          icon: "warning",
          title: "Caracteres no permitidos",
          text: `El campo ${campoNombre} no debe contener números ni caracteres especiales.`,
          toast: true,
          position: "top-end",
          showConfirmButton: false,
          timer: 3000
        });
      }
      this.value = this.value.replace(soloLetrasYEspacios, "");
    });
  }

  function normalizarCampoNumeros(input, campoNombre) {
    if (!input) return;

    const teclasPermitidas = new Set([
      "Backspace",
      "Delete",
      "Tab",
      "ArrowLeft",
      "ArrowRight",
      "Home",
      "End"
    ]);

    input.addEventListener("keydown", function (e) {
      if (e.ctrlKey || e.metaKey) return;
      if (teclasPermitidas.has(e.key)) return;
      if (/^\d$/.test(e.key)) return;
      e.preventDefault();
    });

    input.addEventListener("paste", function (e) {
      e.preventDefault();
      const texto = (e.clipboardData || window.clipboardData).getData("text");
      const numeros = texto.replace(soloNumeros, "").slice(0, 8);
      this.value = numeros;
    });

    input.addEventListener("input", function () {
      const originalValue = this.value;
      if (tieneCaracteresInvalidosNumeros(originalValue)) {
        mostrarAlerta({
          icon: "warning",
          title: "Caracteres no permitidos",
          text: `El campo ${campoNombre} no debe contener letras ni caracteres especiales.`,
          toast: true,
          position: "top-end",
          showConfirmButton: false,
          timer: 3000
        });
      }
      this.value = this.value.replace(soloNumeros, "");
      this.value = this.value.slice(0, 8);
    });
  }

  function validarFechaNacimiento(input) {
    if (!input) return;
    input.addEventListener("change", function () {
      const fecha = this.value;
      if (!fecha) return;

      const nacimiento = new Date(fecha);
      const hoy = new Date();
      hoy.setHours(0, 0, 0, 0);
      nacimiento.setHours(0, 0, 0, 0);

      if (nacimiento > hoy) {
        mostrarAlerta({
          icon: "warning",
          title: "Fecha inválida",
          text: "La fecha de nacimiento no puede ser futura.",
          toast: true,
          position: "top-end",
          showConfirmButton: false,
          timer: 3000
        });
        this.value = "";
        return;
      }

      if (calcularEdad(fecha) < 16) {
        mostrarAlerta({
          icon: "warning",
          title: "Edad insuficiente",
          text: "La edad debe ser mayor o igual a 16 años.",
          toast: true,
          position: "top-end",
          showConfirmButton: false,
          timer: 3000
        });
        this.value = "";
      }
    });
  }

  function obtenerErroresValidacion() {
    const nombre = nombreInput?.value.trim() || "";
    const apellido = apellidoInput?.value.trim() || "";
    const ocupacion = ocupacionInput?.value.trim() || "";
    const telefono = telefonoInput?.value.trim() || "";
    const fecha = fechaInput?.value || "";

    let errorMensaje = "";

    if (tieneCaracteresInvalidosLetras(nombre)) {
      errorMensaje += "Nombre no debe contener números ni caracteres especiales. ";
    }
    if (tieneCaracteresInvalidosLetras(apellido)) {
      errorMensaje += "Apellido no debe contener números ni caracteres especiales. ";
    }
    if (tieneCaracteresInvalidosLetras(ocupacion)) {
      errorMensaje += "Ocupación no debe contener números ni caracteres especiales. ";
    }
    if (tieneCaracteresInvalidosNumeros(telefono)) {
      errorMensaje += "Teléfono no debe contener letras ni caracteres especiales. ";
    }
    if (fecha) {
      const nacimiento = new Date(fecha);
      const hoy = new Date();
      hoy.setHours(0, 0, 0, 0);
      nacimiento.setHours(0, 0, 0, 0);

      if (nacimiento > hoy) {
        errorMensaje += "La fecha de nacimiento no puede ser futura. ";
      } else if (calcularEdad(fecha) < 16) {
        errorMensaje += "La edad debe ser mayor o igual a 16 años. ";
      }
    }

    return { errorMensaje: errorMensaje.trim(), nombre, apellido, ocupacion, telefono, fecha };
  }

  function enfocarPrimerCampoConError({ errorMensaje, nombre, apellido, ocupacion, telefono, fecha }) {
    if (!errorMensaje) return;

    if (tieneCaracteresInvalidosLetras(nombre)) {
      nombreInput.focus();
    } else if (tieneCaracteresInvalidosLetras(apellido)) {
      apellidoInput.focus();
    } else if (tieneCaracteresInvalidosLetras(ocupacion)) {
      ocupacionInput.focus();
    } else if (tieneCaracteresInvalidosNumeros(telefono)) {
      telefonoInput.focus();
    } else if (fecha) {
      fechaInput.focus();
    }
  }

  normalizarCampoLetras(nombreInput, "Nombre");
  normalizarCampoLetras(apellidoInput, "Apellido");
  normalizarCampoLetras(ocupacionInput, "Ocupación");
  normalizarCampoNumeros(telefonoInput, "Teléfono");
  validarFechaNacimiento(fechaInput);

  if (form) {
    let envioConfirmado = false;

    form.addEventListener("submit", function (e) {
      if (envioConfirmado) {
        return;
      }

      e.preventDefault();

      const errores = obtenerErroresValidacion();
      if (errores.errorMensaje) {
        mostrarAlerta({
          icon: "warning",
          title: "Error de validación",
          text: errores.errorMensaje,
          confirmButtonColor: "#198754"
        });
        enfocarPrimerCampoConError(errores);
        return;
      }

      if (typeof Swal !== "undefined") {
        Swal.fire({
          title: "Registro de Paciente",
          text: "¿Deseas guardar el paciente?",
          icon: "question",
          showCancelButton: true,
          confirmButtonColor: "#198754",
          cancelButtonColor: "#d33",
          confirmButtonText: "Sí, guardar",
          cancelButtonText: "Cancelar"
        }).then((result) => {
          if (result.isConfirmed) {
            envioConfirmado = true;
            form.requestSubmit();
          }
        });
      } else if (confirm("¿Deseas guardar el paciente?")) {
        envioConfirmado = true;
        form.requestSubmit();
      }
    });
  }

  contenedor.dataset.validacionIniciada = "true";
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", iniciarValidacionPaciente);
} else {
  iniciarValidacionPaciente();
}
