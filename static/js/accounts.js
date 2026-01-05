const accountsData = document.getElementById('accountsData');

const ADD_URL = accountsData.dataset.addUrl;
const EDIT_URL_TEMPLATE = accountsData.dataset.editUrl;
const DELETE_URL_TEMPLATE = accountsData.dataset.deleteUrl;
const IS_AUTH = accountsData.dataset.isAuthenticated === 'true';

// Add/Edit popup
const openBtn = document.getElementById('openAddAccount');
const overlay = document.getElementById('popupOverlay');
const cancelBtn = document.getElementById('cancelPopup');
const popupTitle = document.getElementById('popupTitle');
const form = document.getElementById('accountForm');
const nameInput = document.getElementById('id_name');
const balanceInput = document.getElementById('id_initial_amount');
const iconInput = document.getElementById('id_icon');

// Delete popup
const deleteOverlay = document.getElementById('deleteOverlay');
const deleteForm = document.getElementById('deleteForm');
const deleteMessage = document.getElementById('deleteMessage');
const cancelDelete = document.getElementById('cancelDelete');

// Login required popup
const loginOverlay = document.getElementById('loginOverlay');
const cancelLogin = document.getElementById('cancelLogin');

function showLoginPopup() {
    loginOverlay.style.display = 'flex';
}

cancelLogin.addEventListener('click', () => loginOverlay.style.display = 'none');

// Add
openBtn.addEventListener('click', () => {
    if (!IS_AUTH) { showLoginPopup(); return; }
    popupTitle.textContent = "Add New Account";
    form.action = ADD_URL;
    nameInput.value = "Untitled";
    balanceInput.value = "0.0";
    iconInput.value = "";
    overlay.style.display = "flex";
});
cancelBtn.addEventListener('click', () => overlay.style.display = "none");

// Edit
document.querySelectorAll('.edit-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        if (!IS_AUTH) { showLoginPopup(); return; }
        const accountId = btn.dataset.id;
        popupTitle.textContent = "Edit Account";
        form.action = EDIT_URL_TEMPLATE.replace('0', accountId);
        nameInput.value = btn.dataset.name;
        balanceInput.value = btn.dataset.balance;
        iconInput.value = btn.dataset.icon;
        overlay.style.display = "flex";
    });
});

// Delete
document.querySelectorAll('.delete-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        if (!IS_AUTH) { showLoginPopup(); return; }
        const accountId = btn.dataset.id;
        const accountName = btn.dataset.name;
        deleteForm.action = DELETE_URL_TEMPLATE.replace('0', accountId);
        deleteMessage.textContent = `Are you sure you want to delete "${accountName}"?`;
        deleteOverlay.style.display = "flex";
    });
});
cancelDelete.addEventListener('click', () => deleteOverlay.style.display = "none");
