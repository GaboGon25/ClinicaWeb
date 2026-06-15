
/**
 * @jest-environment jsdom
 */

describe("Validaciones de Usuario", () => {

  beforeEach(() => {

    document.body.innerHTML =
      '<form>' +
        '<input type="email" name="email" id="correo" />' +
      '</form>';

    global.Swal = {
      fire: jest.fn()
    };

    jest.spyOn(window, "alert").mockImplementation(() => {});

    require("./validando_agregarpc.js");

    document.dispatchEvent(new Event("DOMContentLoaded"));

  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  test("rechaza correo sin arroba", () => {

    const input = document.querySelector("input[name=\"email\"]");

    input.value = "usuariogmail.com";

    input.dispatchEvent(new Event("blur"));

    expect(Swal.fire).toHaveBeenCalled();

  });

});

