document.addEventListener('DOMContentLoaded', function() {
  const form = document.querySelector('form');
  if (form) {
    form.addEventListener('submit', function(e) {
      const inputFechaCita = document.querySelector('input[name="fecha"]');
      const inputHoraCita = document.querySelector('input[name="hora"]');
      const fechaCita = inputFechaCita?.value;
      const horaCita = inputHoraCita?.value;
      const hoy = new Date();
      const yyyy = hoy.getFullYear();
      const mm = String(hoy.getMonth() + 1).padStart(2, '0');
      const dd = String(hoy.getDate()).padStart(2, '0');
      const minDate = yyyy + '-' + mm + '-' + dd;

      if (fechaCita < minDate) {
        e.preventDefault();
        if (typeof Swal !== 'undefined') {
          Swal.fire({
            icon: 'warning',
            title: 'Fecha inválida',
            text: 'No se puede seleccionar una fecha anterior al día de hoy.',
            confirmButtonColor: '#198754'
          });
        } else {
          alert('No se puede seleccionar una fecha anterior al día de hoy.');
        }
        inputFechaCita.focus();
        return;
      }

      if (fechaCita === minDate && horaCita) {
        const ahoraHHMM = String(hoy.getHours()).padStart(2, '0') + ':' + String(hoy.getMinutes()).padStart(2, '0');
        if (horaCita < ahoraHHMM) {
          e.preventDefault();
          if (typeof Swal !== 'undefined') {
            Swal.fire({
              icon: 'warning',
              title: 'Hora inválida',
              text: 'Para fecha de hoy no se permite seleccionar horas previas a la hora actual.',
              confirmButtonColor: '#198754'
            });
          } else {
            alert('Para fecha de hoy no se permite seleccionar horas previas a la hora actual.');
          }
          inputHoraCita.focus();
          return;
        }
      }

      e.preventDefault();
      Swal.fire({
        title: 'Registro de Cita',
        text: '¿Deseas registrar la cita?',
        icon: 'question',
        confirmButtonColor: '#198754',
        cancelButtonColor: '#d33',
        showCancelButton: true,
        confirmButtonText: 'Sí, registrar',
        cancelButtonText: 'Cancelar'
      }).then((result) => {
        if (result.isConfirmed) {
          form.submit();
        }
      });
    });
  }
  // Validación para no permitir fechas pasadas
  var inputFecha = document.querySelector('input[name="fecha"]');
  var inputHora = document.querySelector('input[name="hora"]');
  if (inputFecha) {
    var hoy = new Date();
    var yyyy = hoy.getFullYear();
    var mm = String(hoy.getMonth() + 1).padStart(2, '0');
    var dd = String(hoy.getDate()).padStart(2, '0');
    var minDate = yyyy + '-' + mm + '-' + dd;
    inputFecha.setAttribute('min', minDate);
  }

  function horaActualHHMM() {
    var ahora = new Date();
    var hh = String(ahora.getHours()).padStart(2, '0');
    var mi = String(ahora.getMinutes()).padStart(2, '0');
    return hh + ':' + mi;
  }

  function validarHoraEnTiempoReal() {
    if (!inputFecha || !inputHora) return;
    var fechaSeleccionada = inputFecha.value;
    var horaSeleccionada = inputHora.value;
    if (!fechaSeleccionada || !horaSeleccionada) return;

    var hoy = new Date();
    var fechaHoy = hoy.getFullYear() + '-' + String(hoy.getMonth() + 1).padStart(2, '0') + '-' + String(hoy.getDate()).padStart(2, '0');

    if (fechaSeleccionada === fechaHoy && horaSeleccionada < horaActualHHMM()) {
      if (typeof Swal !== 'undefined') {
        Swal.fire({
          icon: 'warning',
          title: 'Hora inválida',
          text: 'Para fecha de hoy no se puede seleccionar una hora anterior a la hora actual.',
          toast: true,
          position: 'top-end',
          showConfirmButton: false,
          timer: 3000
        });
      } else {
        alert('Para fecha de hoy no se puede seleccionar una hora anterior a la hora actual.');
      }
      inputHora.value = '';
    }
  }

  if (inputHora) {
    inputHora.addEventListener('input', validarHoraEnTiempoReal);
  }

  function validarFechaEnTiempoReal() {
    if (!inputFecha) return;
    var fechaSeleccionada = inputFecha.value;
    if (!fechaSeleccionada) return;

    var hoy = new Date();
    var fechaHoy = hoy.getFullYear() + '-' + String(hoy.getMonth() + 1).padStart(2, '0') + '-' + String(hoy.getDate()).padStart(2, '0');

    if (fechaSeleccionada < fechaHoy) {
      if (typeof Swal !== 'undefined') {
        Swal.fire({
          icon: 'warning',
          title: 'Fecha inválida',
          text: 'No se puede seleccionar una fecha anterior al día de hoy.',
          toast: true,
          position: 'top-end',
          showConfirmButton: false,
          timer: 3000
        });
      } else {
        alert('No se puede seleccionar una fecha anterior al día de hoy.');
      }
      inputFecha.value = '';
      inputFecha.focus();
    }
  }

  if (inputFecha) {
    inputFecha.addEventListener('change', validarHoraEnTiempoReal);
    inputFecha.addEventListener('input', validarFechaEnTiempoReal);
  }
});