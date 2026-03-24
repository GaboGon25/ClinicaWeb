document.addEventListener('DOMContentLoaded', function () {
    const otroCheck = document.getElementById('otroCheck');
    const otroInput = document.getElementById('otroInput');
    const fechaInput = document.querySelector("input[name='fecha']");
    const form = document.querySelector("form");

    otroCheck.addEventListener('change', function () {
      otroInput.style.display = this.checked ? 'inline-block' : 'none';
      if (!this.checked) otroInput.value = '';
    });

    function validarFechaRegistro(input) {
      if (!input) return;
      input.addEventListener("change", function () {
        const fecha = this.value;
        if (!fecha) return;
        const registro = new Date(fecha);
        const hoy = new Date();
        hoy.setHours(0, 0, 0, 0);
        registro.setHours(0, 0, 0, 0);
        if (registro > hoy) {
          const mensaje = "La fecha de registro no puede ser futura.";
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
        }
      });
    }

    validarFechaRegistro(fechaInput);

    if (form) {
      form.addEventListener("submit", function (e) {
        const fecha = fechaInput?.value || "";
        if (fecha) {
          const registro = new Date(fecha);
          const hoy = new Date();
          hoy.setHours(0, 0, 0, 0);
          registro.setHours(0, 0, 0, 0);
          if (registro > hoy) {
            e.preventDefault();
            const mensaje = "La fecha de registro no puede ser futura.";
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
            fechaInput.focus();
          }
        }
      });
    }
  });