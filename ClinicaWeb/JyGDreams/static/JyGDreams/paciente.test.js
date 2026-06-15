/**
 * @jest-environment jsdom
 */
describe("Validaciones del modulo de Paciente", () => {

    beforeAll(() => {
    jest.useFakeTimers();
    jest.setSystemTime(new Date("2024-01-01"));
  });


  beforeEach(() => {
    document.body.innerHTML = `
      <div id="formAgregarPaciente" class="form-container">
        <form>
          <input name="nombre" />
          <input name="apellido" />
          <input name="ocupacion" />
          <input name="telefono" />
          <input name="fecha_nacimiento" />
        </form>
      </div>
    `;

    jest.spyOn(window, "alert").mockImplementation(() => {});

    global.Swal = undefined;

    jest.resetModules();
    require("./validando_agregarpx.js");
  });

  afterEach(() => {
    jest.clearAllMocks();
  });


  //PRUEBAS UNITARIAS PARA VALIDACIONES DE NOMBRE, APELLIDO, OCUPACIÓN Y TELÉFONO
  test("elimina números del campo nombre", () => {
    const input = document.querySelector("input[name='nombre']");

    input.value = "Carlos123";
    input.dispatchEvent(new Event("input"));

    expect(input.value).toBe("Carlos");
  });

  test("el teléfono solo permite números y máximo 8 dígitos", () => {
    const input = document.querySelector("input[name='telefono']");

    input.value = "abc123456789";
    input.dispatchEvent(new Event("input"));

    expect(input.value).toBe("12345678");
  });

  test("calcular la edad a partir de la fecha de nacimiento", () => {
    const { calcularEdad } = require("./validando_agregarpx");
    const edad = calcularEdad("2000-01-01");

  expect(edad).toBe(24);
  });


  //PRUEBAS UNITARIAS PARA VALIDACIONES DE FECHA DE NACIMIENTO
  test("rechaza fecha futura", () => {
  const input = document.querySelector("input[name='fecha_nacimiento']");

  // Crear fecha futura en formato local (SIN ISO)
  const futura = new Date();
  futura.setFullYear(futura.getFullYear() + 1);

  const yyyy = futura.getFullYear();
  const mm = String(futura.getMonth() + 1).padStart(2, "0");
  const dd = String(futura.getDate()).padStart(2, "0");

  input.value = `${yyyy}-${mm}-${dd}`;

  input.dispatchEvent(new Event("change", { bubbles: true }));

  expect(input.value).toBe("");
  expect(window.alert).toHaveBeenCalled();
});

test("rechaza edad menor a 16", () => {
  const input = document.querySelector("input[name='fecha_nacimiento']");

  const menor = new Date();
  menor.setFullYear(menor.getFullYear() - 10);

  const yyyy = menor.getFullYear();
  const mm = String(menor.getMonth() + 1).padStart(2, "0");
  const dd = String(menor.getDate()).padStart(2, "0");

  input.value = `${yyyy}-${mm}-${dd}`;

  input.dispatchEvent(new Event("change", { bubbles: true }));

  expect(input.value).toBe("");
  expect(window.alert).toHaveBeenCalled();
});
   
  test("acepta edad válida (>=16)", () => {
    const input = document.querySelector("input[name='fecha_nacimiento']");

    input.value = "2000-01-01"; // edad válida
    input.dispatchEvent(new Event("change", { bubbles: true }));

    expect(input.value).toBe("2000-01-01");
  });

});