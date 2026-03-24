document.addEventListener("DOMContentLoaded", function () {
  const nombreInput = document.querySelector("input[name='first_name']");
  const apellidoInput = document.querySelector("input[name='last_name']");
  const form = document.querySelector("form");

  const soloLetrasYEspacios = /[^A-Za-zÁÉÍÓÚáéíóúÑñ\s]/g;

  function normalizarCampo(input, campoNombre) {
    if (!input) return;
    input.addEventListener("input", function () {
      const originalValue = this.value;
      if (soloLetrasYEspacios.test(originalValue)) {
        // Mostrar alerta en tiempo real
        const mensaje = `El campo ${campoNombre} no debe contener números ni caracteres especiales.`;
        if (typeof Swal !== "undefined") {
          Swal.fire({
            icon: "warning",
            title: "Caracteres no permitidos",
            text: mensaje,
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            timer: 3000
          });
        } else {
          alert(mensaje);
        }
      }
      this.value = this.value.replace(soloLetrasYEspacios, "");
    });
  }

  normalizarCampo(nombreInput, "Nombre");
  normalizarCampo(apellidoInput, "Apellido");

  const emailInput = document.querySelector("input[name='email']");

  function validarEmail(input) {
    if (!input) return;

    input.addEventListener("blur", function () {
      const valor = this.value.trim();
      if (!valor) return;

      const tieneArroba = valor.includes("@");
      const terminaGmail = valor.toLowerCase().endsWith("@gmail.com");

      if (!tieneArroba || !terminaGmail) {
        const mensaje = "El correo debe incluir '@' y terminar en 'gmail.com'.";

        if (typeof Swal !== "undefined") {
          Swal.fire({
            icon: "warning",
            title: "Correo no válido",
            text: mensaje,
            toast: true,
            position: "top-end",
            showConfirmButton: false,
            timer: 3000
          });
        } else {
          alert(mensaje);
        }
      }
    });
  }

  validarEmail(emailInput);

  if (form) {
    form.addEventListener("submit", function (e) {
      const nombre = nombreInput?.value.trim() || "";
      const apellido = apellidoInput?.value.trim() || "";
      const email = emailInput?.value.trim() || "";

      if (soloLetrasYEspacios.test(nombre) || soloLetrasYEspacios.test(apellido)) {
        e.preventDefault();
        const mensaje = "Nombre y apellido no deben contener números ni caracteres especiales.";

        if (typeof Swal !== "undefined") {
          Swal.fire({
            icon: "warning",
            title: "Error de validación",
            text: mensaje,
            confirmButtonColor: "#198754"
          });
        } else {
          alert(mensaje);
        }

        if (soloLetrasYEspacios.test(nombre)) {
          nombreInput.focus();
        } else if (soloLetrasYEspacios.test(apellido)) {
          apellidoInput.focus();
        }

        return;
      }

      if (emailInput) {
        const tieneArroba = email.includes("@");
        const terminaGmail = email.toLowerCase().endsWith("@gmail.com");

        if (!tieneArroba || !terminaGmail) {
          e.preventDefault();
          const mensaje = "El correo debe incluir '@' y terminar en 'gmail.com'.";

          if (typeof Swal !== "undefined") {
            Swal.fire({
              icon: "warning",
              title: "Error de validación",
              text: mensaje,
              confirmButtonColor: "#198754"
            });
          } else {
            alert(mensaje);
          }

          emailInput.focus();
          return;
        }
      }
    });
  }
});
