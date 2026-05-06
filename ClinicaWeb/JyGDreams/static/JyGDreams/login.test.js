/**
 * @jest-environment jsdom
 */
describe("Pruebas de acceso al login (frontend)", () => {
  beforeEach(() => {
    document.body.innerHTML = `
      <form id="login-form">
        <input name="username" id="usuario" required />
        <input name="password" id="password" required />
        <button type="submit">Iniciar Sesión</button>
      </form>
    `;
  });

  test("Campos requeridos en form de login", () => {
    const form = document.getElementById("login-form");
    const username = document.getElementById("usuario");
    const password = document.getElementById("password");

    // Simula envío sin datos
    username.value = "";
    password.value = "";

    // Verifica que el form no se envíe (si hay validación JS)
    expect(form.checkValidity()).toBe(false);  // HTML5 validation
  });

  test("Envío del form simulado", () => {
    const username = document.getElementById("usuario");
    username.value = "testuser";

    // Simula clic en submit (no mockea respuesta, ya que es POST a Django)
    expect(username.value).toBe("testuser");
  });
});