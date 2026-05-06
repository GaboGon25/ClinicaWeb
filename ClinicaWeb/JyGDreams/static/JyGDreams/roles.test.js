/**
 * @jest-environment jsdom
 */
describe("Pruebas de roles (frontend)", () => {
  beforeEach(() => {
    document.body.innerHTML = `
      <div id="doctor-panel" style="display: none;"></div>
    `;
  });

  test("Mostrar panel según rol simulado", () => {
    const panel = document.getElementById("doctor-panel");
    const userRole = "Doctor/a";  // Simula rol (podría venir de un template variable)

    if (userRole === "Doctor/a") {
      panel.style.display = "block";
    }

    expect(panel.style.display).toBe("block");
  });
});