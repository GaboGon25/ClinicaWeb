document.addEventListener('DOMContentLoaded', function () {
    const otroCheck = document.getElementById('otroCheck');
    const otroInput = document.getElementById('otroInput');

    otroCheck.addEventListener('change', function () {
      otroInput.style.display = this.checked ? 'inline-block' : 'none';
      if (!this.checked) otroInput.value = '';
    });
  });