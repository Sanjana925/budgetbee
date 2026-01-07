// category.js
document.addEventListener("DOMContentLoaded", () => {

    const categoriesData = document.getElementById('categoriesData');
    if (!categoriesData) return;

    const IS_AUTH = categoriesData.dataset.isAuthenticated === 'true';

    // 🚫 GUEST USERS: do nothing, let global.js handle popups
    if (!IS_AUTH) return;

    const ADD_URL = categoriesData.dataset.addUrl;
    const EDIT_URL_TEMPLATE = categoriesData.dataset.editUrl;
    const DELETE_URL_TEMPLATE = categoriesData.dataset.deleteUrl;

    // Auth-only elements
    const overlay = document.getElementById('categoryPopup');
    const deleteOverlay = document.getElementById('deleteCategoryPopup');
    const form = document.getElementById('categoryForm');
    const deleteForm = document.getElementById('deleteCategoryForm');
    const popupTitle = document.getElementById('popupTitle');
    const nameInput = document.getElementById('id_name');
    const iconRadios = document.querySelectorAll('input[name="icon"]');
    const colorRadios = document.querySelectorAll('input[name="color"]');

    // Cancel buttons
    document.getElementById('cancelCategory')?.addEventListener('click', () => overlay?.classList.add('hidden'));
    document.getElementById('cancelDeleteCategory')?.addEventListener('click', () => deleteOverlay?.classList.add('hidden'));

    // Add Category
    document.getElementById('openAddCategory')?.addEventListener('click', () => {
        if (!overlay || !form || !popupTitle || !nameInput) return;
        popupTitle.textContent = "Add Category";
        form.action = ADD_URL;
        nameInput.value = "";
        iconRadios.forEach(r => r.checked = false);
        colorRadios.forEach(r => r.checked = false);
        overlay.classList.remove('hidden');
    });

    // Edit Category
    document.querySelectorAll('.edit-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            if (!overlay || !form || !popupTitle || !nameInput) return;
            const id = btn.dataset.id;
            popupTitle.textContent = "Edit Category";
            form.action = EDIT_URL_TEMPLATE.replace('0', id);
            nameInput.value = btn.dataset.name || "";
            iconRadios.forEach(r => r.checked = r.value === btn.dataset.icon);
            colorRadios.forEach(r => r.checked = r.value === btn.dataset.color);
            overlay.classList.remove('hidden');
        });
    });

    // Delete Category
    document.querySelectorAll('.delete-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            if (!deleteOverlay || !deleteForm) return;
            const id = btn.dataset.id;
            deleteForm.action = DELETE_URL_TEMPLATE.replace('0', id);
            document.getElementById('deleteCategoryMessage').textContent =
                `Are you sure you want to delete "${btn.dataset.name}"?`;
            deleteOverlay.classList.remove('hidden');
        });
    });

    // Submit add/edit
    form?.addEventListener('submit', async e => {
        e.preventDefault();
        try {
            const res = await fetch(form.action, {
                method: 'POST',
                headers: { 'X-Requested-With': 'XMLHttpRequest' },
                body: new FormData(form)
            });
            const result = await res.json();
            if (result.success) window.location.reload();
            else alert(result.error || 'Error saving category');
        } catch {
            alert('Error saving category');
        }
    });

    // Submit delete
    deleteForm?.addEventListener('submit', async e => {
        e.preventDefault();
        try {
            const res = await fetch(deleteForm.action, {
                method: 'POST',
                headers: { 'X-Requested-With': 'XMLHttpRequest' },
                body: new FormData(deleteForm)
            });
            const result = await res.json();
            if (result.success) window.location.reload();
            else alert(result.error || 'Error deleting category');
        } catch {
            alert('Error deleting category');
        }
    });

});
