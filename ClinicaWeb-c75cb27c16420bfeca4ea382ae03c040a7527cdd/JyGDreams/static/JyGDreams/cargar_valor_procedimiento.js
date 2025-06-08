document.addEventListener('DOMContentLoaded', function() {
    // El diccionario de procedimientos debe estar disponible como variable global en el template
    const procedimientos = window.procedimientos_dict || {};

    // Primer procedimiento
    const proc1 = document.getElementById('procedimiento1');
    if (proc1) {
        proc1.addEventListener('change', function() {
            const valor = procedimientos[this.value] || '';
            document.getElementById('valor1').value = valor ? valor.toFixed(2) : '';
        });
    }

    // Segundo procedimiento
    const proc2 = document.getElementById('procedimiento2');
    if (proc2) {
        proc2.addEventListener('change', function() {
            const valor = procedimientos[this.value] || '';
            document.getElementById('valor2').value = valor ? valor.toFixed(2) : '';
        });
    }

    // Checkbox para mostrar/ocultar segundo procedimiento
    const check = document.getElementById('agregarOtroProcedimiento');
    if (check) {
        check.addEventListener('change', function() {
            const otro = document.getElementById('otroProcedimiento');
            const proc2 = document.getElementById('procedimiento2');
            const val2 = document.getElementById('valor2');
            if (this.checked) {
                otro.style.display = '';
                proc2.disabled = false;
                val2.disabled = false;
            } else {
                otro.style.display = 'none';
                proc2.disabled = true;
                val2.disabled = true;
                proc2.value = '';
                val2.value = '';
            }
        });
    }
});