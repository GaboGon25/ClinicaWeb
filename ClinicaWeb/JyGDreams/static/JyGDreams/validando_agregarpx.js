document.addEventListener("DOMContentLoaded", function () {
  const soloLetrasInputs = ["nombre", "apellido", "ocupacion"];
  const telefonoInput = document.querySelector("input[name='telefono']");

  // Solo letras y espacios
  soloLetrasInputs.forEach(function (nombreCampo) {
    const input = document.querySelector(`input[name='${nombreCampo}']`);
    input.addEventListener("input", function () {
      this.value = this.value.replace(/[^A-Za-zÁÉÍÓÚáéíóúÑñ\s]/g, "");
    });
  });

  // Solo números, máximo 8 caracteres
  telefonoInput.addEventListener("input", function () {
    this.value = this.value.replace(/\D/g, ""); // elimina todo lo que no sea dígito
    this.value = this.value.slice(0, 8);        // limita a 8 dígitos
  });

  const btnAgregar = document.getElementById('btnAgregar');
  const formAgregar = document.getElementById('formAgregarPaciente');

  

});