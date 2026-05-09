/**
 * @jest-environment jsdom
 */

describe("Validaciones del modulo de Descuentos", () => {

  beforeAll(() => {
    jest.useFakeTimers();
  });

  beforeEach(() => {
    document.body.innerHTML = `
      <form>
        <span id="monto-final"></span>

        <!-- Procedimiento 1 -->
        <input type="checkbox" class="checkbox-descuento" data-procedimiento-id="1" id="habilitar_descuento_1"/>
        
        <div id="campo_descuento_1" class="campo-descuento" style="display:none;">
          <input 
            id="descuento_1" 
            class="descuento-input" 
            data-procedimiento-id="1" 
            data-costo="100" 
            value="0"
          />
        </div>

        <div id="error_1"></div>
        <span id="subtotal_1"></span>
      </form>
    `;

    // Mock Swal
    global.Swal = {
      fire: jest.fn().mockResolvedValue({ isConfirmed: true })
    };

    jest.spyOn(window, "alert").mockImplementation(() => {});

    // Importar script real
    require('./pago.js');

    document.dispatchEvent(new Event("DOMContentLoaded"));
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  // ================================
  // 🔴 VALIDACIONES DE INPUT
  // ================================

  test("elimina letras del input", () => {
    const input = document.getElementById("descuento_1");

    input.value = "abc123";
    input.dispatchEvent(new Event("input"));

    expect(input.value).toBe("123");
  });

  // test("solo permite un punto decimal", () => {
  //   const input = document.getElementById("descuento_1");

  //   input.value = "12.3.4";
  //   input.dispatchEvent(new Event("input"));

  //   expect(input.value).toBe("12.34");
  // });

  test("limita a 2 decimales", () => {
    const input = document.getElementById("descuento_1");

    input.value = "10.5678";
    input.dispatchEvent(new Event("input"));

    expect(input.value).toBe("10.56");
  });

  test("elimina valores negativos", () => {
    const input = document.getElementById("descuento_1");

    input.value = "-50";
    input.dispatchEvent(new Event("input"));

    expect(input.value).toBe("50");
  });

  // ================================
  // 🔴 VALIDACION EN TIEMPO REAL
  // ================================

  test("muestra error si descuento excede costo", () => {
    const input = document.getElementById("descuento_1");
    const errorDiv = document.getElementById("error_1");

    input.value = "150";
    input.dispatchEvent(new Event("input"));

    expect(errorDiv.style.display).toBe("block");
    expect(input.classList.contains("is-invalid")).toBe(true);
  });

  test("limpia error si valor es válido", () => {
    const input = document.getElementById("descuento_1");
    const errorDiv = document.getElementById("error_1");

    input.value = "50";
    input.dispatchEvent(new Event("input"));

    expect(errorDiv.style.display).toBe("none");
    expect(input.classList.contains("is-invalid")).toBe(false);
  });

  // ================================
  // 🔴 SUBTOTAL
  // ================================

  test("calcula subtotal correctamente", () => {
    const checkbox = document.getElementById("habilitar_descuento_1");
    const input = document.getElementById("descuento_1");
    const subtotal = document.getElementById("subtotal_1");

    checkbox.checked = true;
    input.value = "20";

    input.dispatchEvent(new Event("input"));

    expect(subtotal.textContent).toBe("C$80.00");
  });

  // ================================
  // 🔴 TOTAL GENERAL
  // ================================

  test("actualiza monto final", () => {
    const checkbox = document.getElementById("habilitar_descuento_1");
    const input = document.getElementById("descuento_1");
    const total = document.getElementById("monto-final");

    checkbox.checked = true;
    input.value = "30";

    input.dispatchEvent(new Event("input"));

    expect(total.textContent).toBe("C$70.00");
  });

  // ================================
  // 🔴 CHECKBOX
  // ================================

  test("muestra campo de descuento al activar checkbox", () => {
    const checkbox = document.getElementById("habilitar_descuento_1");
    const campo = document.getElementById("campo_descuento_1");

    checkbox.checked = true;
    checkbox.dispatchEvent(new Event("change"));

    expect(campo.style.display).toBe("block");
  });

  test("oculta campo y reinicia valor al desactivar checkbox", () => {
    const checkbox = document.getElementById("habilitar_descuento_1");
    const input = document.getElementById("descuento_1");
    const campo = document.getElementById("campo_descuento_1");

    checkbox.checked = false;
    input.value = "50";

    checkbox.dispatchEvent(new Event("change"));

    expect(campo.style.display).toBe("none");
    expect(input.value).toBe("0");
  });

  // ================================
  // 🔴 BLUR (validación final)
  // ================================

  test("corrige valor mayor al costo en blur", () => {
    const input = document.getElementById("descuento_1");

    input.value = "200";
    input.dispatchEvent(new Event("blur"));

    expect(input.value).toBe("100.00");
  });

  test("formatea a 2 decimales en blur", () => {
    const input = document.getElementById("descuento_1");

    input.value = "25";
    input.dispatchEvent(new Event("blur"));

    expect(input.value).toBe("25.00");
  });

  // ================================
  // 🔴 SUBMIT
  // ================================

  test("bloquea submit si hay errores", () => {
    const form = document.querySelector("form");
    const input = document.getElementById("descuento_1");

    input.value = "200"; // inválido

    const event = new Event("submit");
    event.preventDefault = jest.fn();

    form.dispatchEvent(event);

    expect(Swal.fire).toHaveBeenCalled();
  });

  test("permite submit si todo es válido", async () => {
    const form = document.querySelector("form");
    const input = document.getElementById("descuento_1");

    input.value = "20";

    const submitMock = jest.spyOn(form, "submit").mockImplementation(() => {});

    const event = new Event("submit");
    event.preventDefault = jest.fn();

    form.dispatchEvent(event);

    await Promise.resolve();

    expect(Swal.fire).toHaveBeenCalled();
    expect(submitMock).toHaveBeenCalled();
  });

});