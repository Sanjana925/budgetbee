// finance/static/js/accounts.js
// Handles add, edit, delete account popups

const accountsData = document.getElementById("accountsData");

const ADD_URL = accountsData.dataset.addUrl;
const EDIT_URL_TEMPLATE = accountsData.dataset.editUrl;
const DELETE_URL_TEMPLATE = accountsData.dataset.deleteUrl;
const IS_AUTH = accountsData.dataset.isAuthenticated === "true";

// Add/Edit popup elements
const openBtn = document.getElementById("openAddAccount");
const overlay = document.getElementById("popupOverlay");
const cancelBtn = document.getElementById("cancelPopup");
const popupTitle = document.getElementById("popupTitle");
const form = document.getElementById("accountForm");
const nameInput = document.getElementById("id_name");
const balanceInput = document.getElementById("id_initial_amount");
const iconInput = document.getElementById("id_icon");

// Delete popup elements
const deleteOverlay = document.getElementById("deleteOverlay");
const deleteForm = document.getElementById("deleteForm");
const deleteMessage = document.getElementById("deleteMessage");
const cancelDelete = document.getElementById("cancelDelete");

// Login required popup
const loginOverlay = document.getElementById("loginOverlay");
const cancelLogin = document.getElementById("cancelLogin");

cancelLogin.addEventListener("click", () => {
    loginOverlay.style.display = "none";
});

function showLoginPopup() {
    loginOverlay.style.display = "flex";
}

// Add account
openBtn.addEventListener("click", () => {
    if (!IS_AUTH) {
        showLoginPopup();
        return;
    }

    popupTitle.textContent = "Add New Account";
    form.action = ADD_URL;
    nameInput.value = "Untitled";
    balanceInput.value = "0.0";
    iconInput.value = "";
    overlay.style.display = "flex";
});

cancelBtn.addEventListener("click", () => {
    overlay.style.display = "none";
});

// Edit account
document.querySelectorAll(".edit-btn").forEach(button => {
    button.addEventListener("click", () => {
        if (!IS_AUTH) {
            showLoginPopup();
            return;
        }

        const accountId = button.dataset.id;

        popupTitle.textContent = "Edit Account";
        form.action = EDIT_URL_TEMPLATE.replace("0", accountId);
        nameInput.value = button.dataset.name;
        balanceInput.value = button.dataset.balance;
        iconInput.value = button.dataset.icon;

        overlay.style.display = "flex";
    });
});

// Delete account
document.querySelectorAll(".delete-btn").forEach(button => {
    button.addEventListener("click", () => {
        if (!IS_AUTH) {
            showLoginPopup();
            return;
        }

        const accountId = button.dataset.id;
        const accountName = button.dataset.name;

        deleteForm.action = DELETE_URL_TEMPLATE.replace("0", accountId);
        deleteMessage.textContent = `Are you sure you want to delete "${accountName}"?`;
        deleteOverlay.style.display = "flex";
    });
});

cancelDelete.addEventListener("click", () => {
    deleteOverlay.style.display = "none";
});
