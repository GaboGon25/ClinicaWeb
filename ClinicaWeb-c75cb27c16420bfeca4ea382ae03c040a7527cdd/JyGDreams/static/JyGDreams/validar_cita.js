document.addEventListener("DOMContentLoaded", function () {
  const checkbox = document.getElementById("agregarOtroProcedimiento");
  const otroProcedimiento = document.getElementById("otroProcedimiento");
  const procedimiento2 = document.querySelector("select[name='procedimiento2']");
  const valor2 = document.querySelector("input[name='valor2']");

  checkbox.addEventListener("change", function () {
    const checked = this.checked;
    otroProcedimiento.style.display = checked ? "flex" : "none";
    procedimiento2.disabled = !checked;
    valor2.disabled = !checked;
  });
});