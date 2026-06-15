
/**
 * @jest-environment jsdom
 */

describe("Validaciones de Expediente", () => {

  beforeAll(() => {
    jest.useFakeTimers();
    jest.setSystemTime(new Date("2026-05-10"));
  });

  beforeEach(() => {

    document.body.innerHTML =
      '<form>' +
        '<input type="checkbox" id="otroCheck" />' +
        '<input type="text" id="otroInput" />' +
        '<input type="date" name="fecha" id="fecha_registro" />' +
      '</form>';

    global.Swal = {
      fire: jest.fn()
    };

    jest.spyOn(window, "alert").mockImplementation(() => {});

    require("./validaciones_expediente.js");

    document.dispatchEvent(new Event("DOMContentLoaded"));

  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  // test("rechaza fecha futura", () => {

  //   const input = document.querySelector("input[name=\"fecha\"]");

  //   input.value = "2026-05-15";

  //   input.dispatchEvent(new Event("change"));

  //   expect(Swal.fire).toHaveBeenCalled();

  //   expect(input.value).toBe("");

  // });

  test("acepta fecha actual", () => {

    const input = document.querySelector("input[name=\"fecha\"]");

    input.value = "2026-05-10";

    input.dispatchEvent(new Event("change"));

    expect(Swal.fire).not.toHaveBeenCalled();

    expect(input.value).toBe("2026-05-10");

  });

});

