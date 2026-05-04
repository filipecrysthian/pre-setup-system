/**
 * PRÉ SETUP System - Main JavaScript
 */

function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    if (sidebar) sidebar.classList.toggle('show');
}

document.addEventListener('click', function (e) {
    const sidebar = document.getElementById('sidebar');
    const toggle = document.querySelector('.sidebar-toggle');
    if (sidebar && toggle && window.innerWidth < 992) {
        if (!sidebar.contains(e.target) && !toggle.contains(e.target)) {
            sidebar.classList.remove('show');
        }
    }
});

document.addEventListener('DOMContentLoaded', function () {
    // Auto-dismiss alerts after 5s
    document.querySelectorAll('.alert-dismissible').forEach(function (alert) {
        setTimeout(function () {
            var bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) bsAlert.close();
        }, 5000);
    });

    // Bootstrap tooltips
    document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(function (el) {
        new bootstrap.Tooltip(el);
    });

    // Setup form progress
    initSetupProgress();
});

function initSetupProgress() {
    var bar = document.getElementById('setupProgressBar');
    var txt = document.getElementById('setupProgressText');
    if (!bar || !txt) return;

    var selects = document.querySelectorAll('select[name^="status_"]');
    var total = selects.length;

    function update() {
        var filled = 0;
        selects.forEach(function (s) { if (s.value) filled++; });
        var pct = total > 0 ? Math.round((filled / total) * 100) : 0;
        bar.style.width = pct + '%';
        bar.setAttribute('aria-valuenow', pct);
        txt.textContent = filled + ' / ' + total + ' itens preenchidos';

        selects.forEach(function (s) {
            var row = s.closest('.setup-item-row');
            if (!row) return;
            row.classList.remove('status-ok-border', 'status-pending-border', 'status-na-border');
            if (s.value === 'OK') row.classList.add('status-ok-border');
            else if (s.value === 'PENDENTE') row.classList.add('status-pending-border');
            else if (s.value === 'N/A') row.classList.add('status-na-border');
        });
    }

    selects.forEach(function (s) { s.addEventListener('change', update); });
    update();
}

function validateSetupForm(form) {
    var selects = form.querySelectorAll('select[name^="status_"]');
    var valid = true;
    selects.forEach(function (sel) {
        if (!sel.value) { valid = false; sel.classList.add('is-invalid'); }
        else { sel.classList.remove('is-invalid'); }
        if (sel.value === 'PENDENTE') {
            var id = sel.name.replace('status_', '');
            var obs = form.querySelector('textarea[name="observation_' + id + '"]');
            if (obs && !obs.value.trim()) { valid = false; obs.classList.add('is-invalid'); }
            else if (obs) { obs.classList.remove('is-invalid'); }
        }
    });
    if (!valid) alert('Preencha todos os campos obrigatórios. Itens PENDENTE requerem observação.');
    return valid;
}
