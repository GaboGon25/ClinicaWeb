document.addEventListener("DOMContentLoaded", function () {
  const nombreInput = document.querySelector("input[name='nombre']");
  const apellidoInput = document.querySelector("input[name='apellido']");
  const ocupacionInput = document.querySelector("input[name='ocupacion']");
  const telefonoInput = document.querySelector("input[name='telefono']");
  const fechaInput = document.querySelector("input[name='fecha_nacimiento']");
  const form = document.querySelector("form");

  const soloLetrasYEspacios = /[^A-Za-zÁÉÍÓÚáéíóúÑñ\s]/g;
  const soloNumeros = /\D/g;

  function calcularEdad(fechaNacimiento) {
    const hoy = new Date();
    const nacimiento = new Date(fechaNacimiento);
    let edad = hoy.getFullYear() - nacimiento.getFullYear();
    const mes = hoy.getMonth() - nacimiento.getMonth();
    if (mes < 0 || (mes === 0 && hoy.getDate() < nacimiento.getDate())) {
      edad--;
    }
    return edad;
  }

  function normalizarCampoLetras(input, campoNombre) {
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

  function normalizarCampoNumeros(input, campoNombre) {
    if (!input) return;
    input.addEventListener("input", function () {
      const originalValue = this.value;
      if (soloNumeros.test(originalValue)) {
        // Mostrar alerta en tiempo real
        const mensaje = `El campo ${campoNombre} no debe contener letras ni caracteres especiales.`;
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
      this.value = this.value.replace(soloNumeros, "");
      this.value = this.value.slice(0, 8); // limita a 8 dígitos
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
        const mensaje = "La fecha de nacimiento no puede ser futura.";
        if (typeof Swal !== "undefined") {
          Swal.fire({
            icon: "warning",
            title: "Fecha inválida",
            text: mensaje,
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            timer: 3000
          });
        } else {
          alert(mensaje);
        }
        this.value = "";
        return;
      }
      const edad = calcularEdad(fecha);
      if (edad < 16) {
        const mensaje = "La edad debe ser mayor o igual a 16 años.";
        if (typeof Swal !== "undefined") {
          Swal.fire({
            icon: "warning",
            title: "Edad insuficiente",
            text: mensaje,
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            timer: 3000
          });
        } else {
          alert(mensaje);
        }
        this.value = "";
      }
    });
  }

  normalizarCampoLetras(nombreInput, "Nombre");
  normalizarCampoLetras(apellidoInput, "Apellido");
  normalizarCampoLetras(ocupacionInput, "Ocupación");
  normalizarCampoNumeros(telefonoInput, "Teléfono");
  validarFechaNacimiento(fechaInput);

  if (form) {
    form.addEventListener("submit", function (e) {
      const nombre = nombreInput?.value.trim() || "";
      const apellido = apellidoInput?.value.trim() || "";
      const ocupacion = ocupacionInput?.value.trim() || "";
      const telefono = telefonoInput?.value.trim() || "";
      const fecha = fechaInput?.value || "";

      let errorMensaje = "";
      if (soloLetrasYEspacios.test(nombre)) {
        errorMensaje += "Nombre no debe contener números ni caracteres especiales. ";
      }
      if (soloLetrasYEspacios.test(apellido)) {
        errorMensaje += "Apellido no debe contener números ni caracteres especiales. ";
      }
      if (soloLetrasYEspacios.test(ocupacion)) {
        errorMensaje += "Ocupación no debe contener números ni caracteres especiales. ";
      }
      if (soloNumeros.test(telefono)) {
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

      if (errorMensaje) {
        e.preventDefault();
        if (typeof Swal !== "undefined") {
          Swal.fire({
            icon: "warning",
            title: "Error de validación",
            text: errorMensaje.trim(),
            confirmButtonColor: "#198754"
          });
        } else {
          alert(errorMensaje.trim());
        }

        // Enfocar el primer campo con error
        if (soloLetrasYEspacios.test(nombre)) {
          nombreInput.focus();
        } else if (soloLetrasYEspacios.test(apellido)) {
          apellidoInput.focus();
        } else if (soloLetrasYEspacios.test(ocupacion)) {
          ocupacionInput.focus();
        } else if (soloNumeros.test(telefono)) {
          telefonoInput.focus();
        } else if (fecha && (new Date(fecha) > new Date() || calcularEdad(fecha) < 16)) {
          fechaInput.focus();
        }
      }
    });
  }
});