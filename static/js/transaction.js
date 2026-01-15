document.addEventListener("DOMContentLoaded", function () {
    const btn = document.getElementById("newTransactionBtn");
    if (btn) btn.addEventListener("click", () => openModal());

    // Delegated click for edit/delete buttons and type toggle
    document.body.addEventListener("click", function (e) {
        // ---------- Edit transaction ----------
        if (e.target.matches(".edit-transaction")) {
            const txId = e.target.dataset.id;
            openModal(txId);
        }

        // ---------- Delete transaction ----------
        if (e.target.matches(".delete-transaction")) {
            const txId = e.target.dataset.id;
            deleteTransaction(txId);
        }

        // ---------- Type toggle (Income/Expense) ----------
        if (e.target.matches(".type-toggle .toggle-btn")) {
            const btn = e.target;
            const type = btn.dataset.type;

            // Activate clicked button
            btn.parentElement.querySelectorAll(".toggle-btn").forEach(b => b.classList.remove("active"));
            btn.classList.add("active");

            // Update hidden input
            const typeInput = document.getElementById("typeInput");
            if (typeInput) typeInput.value = type;

            // Filter category dropdown
            const categorySelect = document.getElementById("categorySelect");
            if (categorySelect) {
                Array.from(categorySelect.options).forEach(opt => {
                    opt.style.display = opt.dataset.type === type ? "" : "none";
                });

                // Select first visible category automatically
                const firstVisible = Array.from(categorySelect.options).find(o => o.style.display !== "none");
                if (firstVisible) categorySelect.value = firstVisible.value;
            }
        }
    });
});

// ---------------- CSRF Helper ----------------
function getCSRFToken() {
    const name = "csrftoken";
    const cookies = document.cookie.split(";").map(c => c.trim());
    for (let c of cookies) {
        if (c.startsWith(name + "=")) return decodeURIComponent(c.slice(name.length + 1));
    }
    return null;
}

// ---------------- Open Modal ----------------
function openModal(txId = null) {
    closeModal();

    let url = "/transaction/";
    if (txId) url = `/transaction/edit/${txId}/`;

    fetch(url)
        .then(res => res.ok ? res.text() : Promise.reject("Failed to load modal"))
        .then(html => {
            document.body.insertAdjacentHTML("beforeend", html);
            document.body.classList.add("modal-open");

            const form = document.getElementById("transactionForm");
            if (!form) return;

            // ---------- Set default type toggle and filter categories ----------
            const typeInput = document.getElementById("typeInput");
            const categorySelect = document.getElementById("categorySelect");
            if (typeInput && categorySelect) {
                const defaultType = typeInput.value || "income";
                const toggleBtns = document.querySelectorAll(".type-toggle .toggle-btn");

                toggleBtns.forEach(btn => {
                    const btnType = btn.dataset.type;
                    btn.classList.toggle("active", btnType === defaultType);
                });

                // Filter categories
                Array.from(categorySelect.options).forEach(opt => {
                    opt.style.display = opt.dataset.type === defaultType ? "" : "none";
                });

                // Select first visible category automatically
                const firstVisible = Array.from(categorySelect.options).find(o => o.style.display !== "none");
                if (firstVisible) categorySelect.value = firstVisible.value;
            }

            // ---------- Form submit ----------
            form.addEventListener("submit", function (e) {
                e.preventDefault();
                const data = new FormData(form);
                const postUrl = txId ? `/transaction/edit/${txId}/` : "/transaction/";

                fetch(postUrl, {
                    method: "POST",
                    body: data,
                    headers: {
                        "X-Requested-With": "XMLHttpRequest",
                        "X-CSRFToken": getCSRFToken()
                    },
                })
                .then(res => res.json())
                .then(res => {
                    if (res.success) {
                        updateTransactionList(res.transaction);
                        closeModal();
                    } else if (res.error === "login_required") {
                        window.location.href = "/userauths/login/";
                    } else {
                        console.error(res.error);
                        alert(res.error);
                    }
                })
                .catch(err => console.error("Error submitting transaction:", err));
            });
        })
        .catch(err => console.error("Failed to load modal:", err));
}

// ---------------- Delete Transaction ----------------
function deleteTransaction(txId) {
    if (!confirm("Are you sure you want to delete this transaction?")) return;

    fetch(`/transaction/delete/${txId}/`, {
        method: "POST",
        headers: {
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": getCSRFToken()
        },
    })
    .then(res => res.json())
    .then(res => {
        if (res.success) {
            const txItem = document.querySelector(`.transaction-item[data-id="${txId}"]`);
            if (txItem) {
                const dateCard = txItem.closest(".date-card");
                txItem.remove();
                if (dateCard && dateCard.querySelectorAll(".transaction-item").length === 0) {
                    dateCard.remove();
                }
                updateTopSummary(res);
            }

            const container = document.getElementById("transactionsContainer");
            const emptyState = document.getElementById("emptyState");
            if (container && container.children.length === 0 && emptyState) {
                emptyState.style.display = "flex";
            }
        } else {
            console.error(res.error);
            alert(res.error);
        }
    })
    .catch(err => console.error("Error deleting transaction:", err));
}

// ---------------- Close Modal ----------------
function closeModal() {
    const modal = document.getElementById("transactionModal");
    if (modal) modal.remove();
    document.body.classList.remove("modal-open");
}

// ---------------- Update Transaction List ----------------
function updateTransactionList(tx) {
    if (!tx || !tx.date) return;

    const container = document.getElementById("transactionsContainer");
    if (!container) return;

    const emptyState = document.getElementById("emptyState");
    if (emptyState) emptyState.style.display = "none";

    let dateCard = container.querySelector(`[data-date="${tx.date}"]`);
    if (!dateCard) {
        dateCard = document.createElement("div");
        dateCard.classList.add("date-card");
        dateCard.dataset.date = tx.date;

        dateCard.innerHTML = `
            <div class="date-header">
                <span class="date-label">${tx.date}</span>
                <span class="summary">Income: Rs. 0.00 | Expense: Rs. 0.00</span>
            </div>
            <div class="transaction-list"></div>
        `;

        const existingCards = Array.from(container.querySelectorAll(".date-card"));
        const inserted = existingCards.find(c => new Date(c.dataset.date) < new Date(tx.date));
        if (inserted) container.insertBefore(dateCard, inserted);
        else container.appendChild(dateCard);
    }

    const list = dateCard.querySelector(".transaction-list");

    let txItem = list.querySelector(`[data-id="${tx.id}"]`);
    if (!txItem) {
        txItem = document.createElement("div");
        txItem.classList.add("transaction-item");
        txItem.dataset.id = tx.id;
        list.insertBefore(txItem, list.firstChild);
    }

    txItem.innerHTML = `
        <span class="category"><i class="icon">${tx.category_icon}</i> ${tx.category_name}</span>
        <span class="amount ${tx.type}">${tx.type === "income" ? "+" : "-"} Rs. ${parseFloat(tx.amount).toFixed(2)}</span>
        <button class="edit-transaction" data-id="${tx.id}">✏️</button>
        <button class="delete-transaction" data-id="${tx.id}">🗑️</button>
    `;

    updateDateSummary(dateCard);
    updateTopSummary(tx);
}

// ---------------- Update Date Summary ----------------
function updateDateSummary(dateCard) {
    if (!dateCard) return;
    const items = dateCard.querySelectorAll(".transaction-item");
    let income = 0, expense = 0;

    items.forEach(item => {
        const amtElem = item.querySelector(".amount");
        if (!amtElem) return;
        const amtText = amtElem.textContent.replace(/[^\d.]/g, "");
        const amt = parseFloat(amtText) || 0;
        if (amtElem.classList.contains("income")) income += amt;
        else expense += amt;
    });

    const summary = dateCard.querySelector(".summary");
    if (summary) summary.textContent = `Income: Rs. ${income.toFixed(2)} | Expense: Rs. ${expense.toFixed(2)}`;
}

// ---------------- Update Top Summary ----------------
function updateTopSummary(data) {
    const amounts = document.querySelectorAll(".summary-left .amount");
    if (amounts.length >= 2) {
        amounts[0].innerText = "Rs. " + parseFloat(data.total_income || 0).toFixed(2);
        amounts[1].innerText = "Rs. " + parseFloat(data.total_expense || 0).toFixed(2);
    }
    const balanceElem = document.querySelector(".summary-right .balance-amount");
    if (balanceElem) {
        balanceElem.innerText = "Rs. " + parseFloat(data.balance || 0).toFixed(2);
    }
}
