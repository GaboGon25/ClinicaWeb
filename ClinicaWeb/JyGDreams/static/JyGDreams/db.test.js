describe("Pruebas de datos en frontend (sin API)", () => {
  test("Procesamiento de datos simulados", () => {
    // Simula datos que vendrían de un template (no de DB)
    const pacientes = [{ nombre: "Juan", apellido: "Pérez" }];
    
    // Prueba lógica JS (ej. filtrar)
    const filtrados = pacientes.filter(p => p.nombre === "Juan");
    expect(filtrados.length).toBe(1);
  });
});