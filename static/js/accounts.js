document.addEventListener("DOMContentLoaded", () => {

    const accountsData = document.getElementById('accountsData');
    if (!accountsData) return;

    const IS_AUTH = accountsData.dataset.isAuthenticated === 'true';
console.log("IS_AUTH:", IS_AUTH);
console.log("Add button:", document.getElementById('openAddAccount'));
console.log("Edit buttons:", document.querySelectorAll('.edit-btn'));
console.log("Delete buttons:", document.querySelectorAll('.delete-btn'));

    // 🚫 GUEST USERS: do nothing, let global.js handle popups
    if (!IS_AUTH) return;

    const ADD_URL = accountsData.dataset.addUrl;
    const EDIT_URL_TEMPLATE = accountsData.dataset.editUrl;
    const DELETE_URL_TEMPLATE = accountsData.dataset.deleteUrl;

    // Auth-only elements
    const overlay = document.getElementById('popupOverlay');
    const deleteOverlay = document.getElementById('deleteOverlay');
    const form = document.getElementById('accountForm');
    const deleteForm = document.getElementById('deleteForm');
    const popupTitle = document.getElementById('popupTitle');

    const nameInput = document.getElementById('id_name');
    const balanceInput = document.getElementById('id_initial_amount');
    const iconRadios = document.querySelectorAll('input[name="icon"]');

    // Cancel buttons
    document.getElementById('cancelPopup')?.addEventListener('click', () => {
        overlay.classList.add('hidden');
    });

    document.getElementById('cancelDelete')?.addEventListener('click', () => {
        deleteOverlay.classList.add('hidden');
    });

    // Add Account
    document.getElementById('openAddAccount')?.addEventListener('click', () => {
        popupTitle.textContent = "Add New Account";
        form.action = ADD_URL;
        nameInput.value = "Untitled";
        balanceInput.value = 0.0;
        iconRadios.forEach(r => r.checked = false);
        overlay.classList.remove('hidden');
    });

    // Edit
    document.querySelectorAll('.edit-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const id = btn.dataset.id;
            popupTitle.textContent = "Edit Account";
            form.action = EDIT_URL_TEMPLATE.replace('0', id);
            nameInput.value = btn.dataset.name;
            balanceInput.value = btn.dataset.balance;
            iconRadios.forEach(r => r.checked = r.value === btn.dataset.icon);
            overlay.classList.remove('hidden');
        });
    });

    // Delete
    document.querySelectorAll('.delete-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const id = btn.dataset.id;
            deleteForm.action = DELETE_URL_TEMPLATE.replace('0', id);
            document.getElementById('deleteMessage').textContent =
                `Are you sure you want to delete "${btn.dataset.name}"?`;
            deleteOverlay.classList.remove('hidden');
        });
    });

    // Submit add/edit
    form.addEventListener('submit', async e => {
        e.preventDefault();
        const res = await fetch(form.action, {
            method: 'POST',
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
            body: new FormData(form)
        });
        const result = await res.json();
        if (result.success) window.location.reload();
        else alert(result.error || 'Error saving account');
    });

    // Submit delete
    deleteForm.addEventListener('submit', async e => {
        e.preventDefault();
        const res = await fetch(deleteForm.action, {
            method: 'POST',
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
            body: new FormData(deleteForm)
        });
        const result = await res.json();
        if (result.success) window.location.reload();
        else alert(result.error || 'Error deleting account');
    });

});

