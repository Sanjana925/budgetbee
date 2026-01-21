document.addEventListener("DOMContentLoaded", () => {

    // Open "New Transaction" modal
    const btn = document.getElementById("newTransactionBtn");
    if (btn) btn.addEventListener("click", () => openModal());

    // Delegated click handling
    document.body.addEventListener("click", e => {

        // Edit transaction
        if (e.target.matches(".edit-transaction")) {
            openModal(e.target.dataset.id);
        }

        // Delete transaction
        if (e.target.matches(".delete-transaction")) {
            deleteTransaction(e.target.dataset.id);
        }

        // Type toggle (Income/Expense)
        if (e.target.matches(".type-toggle .toggle-btn")) {
            const type = e.target.dataset.type;
            e.target.parentElement.querySelectorAll(".toggle-btn").forEach(b => b.classList.remove("active"));
            e.target.classList.add("active");

            const typeInput = document.getElementById("typeInput");
            if (typeInput) typeInput.value = type;

            const categorySelect = document.getElementById("categorySelect");
            if (categorySelect) {
                Array.from(categorySelect.options).forEach(opt => {
                    opt.style.display = opt.dataset.type === type ? "" : "none";
                });
                const firstVisible = Array.from(categorySelect.options).find(o => o.style.display !== "none");
                if (firstVisible) categorySelect.value = firstVisible.value;
            }
        }
    });
});

// CSRF Helper
function getCSRFToken() {
    const name = "csrftoken";
    const cookies = document.cookie.split(";").map(c => c.trim());
    for (let c of cookies) if (c.startsWith(name + "=")) return decodeURIComponent(c.slice(name.length + 1));
    return null;
}

// Open Modal
function openModal(txId = null) {
    closeModal();
    let url = txId ? `/transaction/edit/${txId}/` : "/transaction/";

    fetch(url)
        .then(res => res.ok ? res.text() : Promise.reject("Failed to load modal"))
        .then(html => {
            document.body.insertAdjacentHTML("beforeend", html);
            document.body.classList.add("modal-open");

            const form = document.getElementById("transactionForm");
            if (!form) return;

            const typeInput = document.getElementById("typeInput");
            const categorySelect = document.getElementById("categorySelect");
            if (typeInput && categorySelect) {
                const defaultType = typeInput.value || "income";
                document.querySelectorAll(".type-toggle .toggle-btn").forEach(btn => {
                    btn.classList.toggle("active", btn.dataset.type === defaultType);
                });
                Array.from(categorySelect.options).forEach(opt => {
                    opt.style.display = opt.dataset.type === defaultType ? "" : "none";
                });
                const firstVisible = Array.from(categorySelect.options).find(o => o.style.display !== "none");
                if (firstVisible) categorySelect.value = firstVisible.value;
            }

            // Form submit
            form.addEventListener("submit", e => {
                e.preventDefault();
                const data = new FormData(form);
                const postUrl = txId ? `/transaction/edit/${txId}/` : "/transaction/";

                fetch(postUrl, {
                    method: "POST",
                    body: data,
                    headers: {
                        "X-Requested-With": "XMLHttpRequest",
                        "X-CSRFToken": getCSRFToken()
                    }
                })
                .then(res => res.json())
                .then(res => {
                    if (res.success) {
                        updateTransactionList(res.transaction);
                        closeModal();

                        // Dispatch event to update budgets
                        window.dispatchEvent(new CustomEvent("transaction:changed", {
                            detail: {
                                transaction: {
                                    category_id: res.transaction.category_id || res.transaction.category,
                                    amount: parseFloat(res.transaction.amount),
                                    type: (res.transaction.type || "expense").toLowerCase()
                                },
                                action: txId ? "edit" : "add"
                            }
                        }));
                    } else if (res.error === "login_required") {
                        window.location.href = "/userauths/login/";
                    } else {
                        alert(res.error || "Failed to save transaction.");
                        console.error(res.error);
                    }
                })
                .catch(err => console.error("Error submitting transaction:", err));
            });
        })
        .catch(err => console.error("Failed to load modal:", err));
}

// Delete Transaction
function deleteTransaction(txId) {
    if (!confirm("Are you sure you want to delete this transaction?")) return;

    fetch(`/transaction/delete/${txId}/`, {
        method: "POST",
        headers: {
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": getCSRFToken()
        }
    })
    .then(res => res.json())
    .then(res => {
        if (res.success) {
            const txItem = document.querySelector(`.transaction-item[data-id="${txId}"]`);
            if (txItem) {
                const dateCard = txItem.closest(".date-card");
                txItem.remove();
                if (dateCard && dateCard.querySelectorAll(".transaction-item").length === 0) dateCard.remove();

                updateTopSummary(res);

                // Dispatch budget update
                window.dispatchEvent(new CustomEvent("transaction:changed", {
                    detail: {
                        transaction: {
                            category_id: res.category_id,
                            amount: parseFloat(res.amount),
                            type: "expense"
                        },
                        action: "delete"
                    }
                }));
            }

            const container = document.getElementById("transactionsContainer");
            const emptyState = document.getElementById("emptyState");
            if (container && container.children.length === 0 && emptyState) emptyState.style.display = "flex";
        } else {
            alert(res.error || "Failed to delete transaction.");
            console.error(res.error);
        }
    })
    .catch(err => console.error("Error deleting transaction:", err));
}

// Close Modal
function closeModal() {
    const modal = document.getElementById("transactionModal");
    if (modal) modal.remove();
    document.body.classList.remove("modal-open");
}

// Update Transaction List
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

// Update Date Summary
function updateDateSummary(dateCard) {
    if (!dateCard) return;
    let income = 0, expense = 0;

    dateCard.querySelectorAll(".transaction-item").forEach(item => {
        const amtElem = item.querySelector(".amount");
        if (!amtElem) return;

        const amt = parseFloat(amtElem.textContent.replace(/[^\d.]/g, "")) || 0;
        if (amtElem.classList.contains("income")) income += amt;
        else expense += amt;
    });

    const summary = dateCard.querySelector(".summary");
    if (summary) summary.textContent = `Income: Rs. ${income.toFixed(2)} | Expense: Rs. ${expense.toFixed(2)}`;
}

// Update Top Summary
function updateTopSummary(data) {
    const amounts = document.querySelectorAll(".summary-left .amount");
    if (amounts.length >= 2) {
        amounts[0].innerText = "Rs. " + parseFloat(data.total_income || 0).toFixed(2);
        amounts[1].innerText = "Rs. " + parseFloat(data.total_expense || 0).toFixed(2);
    }

    const balanceElem = document.querySelector(".summary-right .balance-amount");
    if (balanceElem) balanceElem.innerText = "Rs. " + parseFloat(data.balance || 0).toFixed(2);
}
