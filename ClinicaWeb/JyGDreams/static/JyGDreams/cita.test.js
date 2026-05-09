/**
 * @jest-environment jsdom
 */

describe("Validaciones del módulo de Citas", () => {

  beforeAll(() => {
    jest.useFakeTimers();
    jest.setSystemTime(new Date("2026-05-06T10:00:00")); // fecha controlada
  });

  beforeEach(() => {
    document.body.innerHTML = `
      <form>
        <input name="fecha" />
        <input name="hora" />
      </form>
    `;

    // Mock Swal
    global.Swal = {
      fire: jest.fn().mockResolvedValue({ isConfirmed: true })
    };

    jest.spyOn(window, "alert").mockImplementation(() => {});

    // IMPORTANTE: cambia esta ruta por la real
    require('./validaciones_cita.js');

    document.dispatchEvent(new Event("DOMContentLoaded"));
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  
  // VALIDACIÓN DE FECHA PASADA (SUBMIT)
 

  test("rechaza fecha menor a hoy", () => {
    const form = document.querySelector("form");
    const inputFecha = document.querySelector("input[name='fecha']");
    const inputHora = document.querySelector("input[name='hora']");

    inputFecha.value = "2026-05-05"; // ayer
    inputHora.value = "12:00";

    const event = new Event("submit");
    event.preventDefault = jest.fn();

    form.dispatchEvent(event);

    expect(event.preventDefault).toHaveBeenCalled();
    expect(Swal.fire).toHaveBeenCalled();
  });

  
  // VALIDACIÓN DE HORA PASADA
  

  test("rechaza hora pasada en fecha actual", () => {
    const form = document.querySelector("form");
    const inputFecha = document.querySelector("input[name='fecha']");
    const inputHora = document.querySelector("input[name='hora']");

    inputFecha.value = "2026-05-06"; // hoy
    inputHora.value = "08:00"; // menor a 10:00

    const event = new Event("submit");
    event.preventDefault = jest.fn();

    form.dispatchEvent(event);

    expect(event.preventDefault).toHaveBeenCalled();
    expect(Swal.fire).toHaveBeenCalled();
  });


  // CONFIRMACIÓN DE REGISTRO
 

  test("permite submit si datos son válidos", async () => {
    const form = document.querySelector("form");
    const inputFecha = document.querySelector("input[name='fecha']");
    const inputHora = document.querySelector("input[name='hora']");

    inputFecha.value = "2026-05-06";
    inputHora.value = "12:00";

    const submitMock = jest.spyOn(form, "submit").mockImplementation(() => {});

    const event = new Event("submit");
    event.preventDefault = jest.fn();

    form.dispatchEvent(event);

    await Promise.resolve();

    expect(Swal.fire).toHaveBeenCalled();
    expect(submitMock).toHaveBeenCalled();
  });


 
  //  VALIDACIÓN EN TIEMPO REAL (HORA)
 

  test("limpia hora si es menor a la actual (input event)", () => {
    const inputFecha = document.querySelector("input[name='fecha']");
    const inputHora = document.querySelector("input[name='hora']");

    inputFecha.value = "2026-05-06";
    inputHora.value = "08:00";

    inputHora.dispatchEvent(new Event("input"));

    expect(inputHora.value).toBe("");
    expect(Swal.fire).toHaveBeenCalled();
  });

  //  VALIDACIÓN EN TIEMPO REAL (FECHA)
  

  test("limpia fecha si es menor a hoy", () => {
    const inputFecha = document.querySelector("input[name='fecha']");

    inputFecha.value = "2026-05-05";

    inputFecha.dispatchEvent(new Event("input"));

    expect(inputFecha.value).toBe("");
    expect(Swal.fire).toHaveBeenCalled();
  });

 
  
  // test("no valida si fecha u hora están vacías", () => {
  //   const inputHora = document.querySelector("input[name='hora']");

  //   inputHora.value = "";
  //   inputHora.dispatchEvent(new Event("input"));

  //   expect(Swal.fire).not.toHaveBeenCalled();
  // });

});