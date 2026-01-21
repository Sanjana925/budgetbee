document.addEventListener("DOMContentLoaded", () => {

    // -------------------------------
    // 1️⃣ Grab budget data from home.html
    // -------------------------------
    let budgetsData = {};
    const budgetsEl = document.getElementById("budgetsData");
    if (budgetsEl) {
        budgetsData = JSON.parse(budgetsEl.textContent);
        window.budgetsData = budgetsData; // store globally for alerts
        console.log("💰 Loaded budgets data", budgetsData);
    }

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
    closeModal(); // close any existing modal
    let url = txId ? `/transaction/edit/${txId}/` : "/transaction/";

    fetch(url)
        .then(res => res.ok ? res.text() : Promise.reject("Failed to load modal"))
        .then(html => {
            document.body.insertAdjacentHTML("beforeend", html);
            document.body.classList.add("modal-open");
            console.log("📦 Transaction modal loaded");

            const form = document.getElementById("transactionForm");
            if (!form) return console.error("❌ transactionForm not found");

            if (!document.getElementById("formError")) {
                const errorDiv = document.createElement("div");
                errorDiv.id = "formError";
                errorDiv.style.color = "#e53935";
                errorDiv.style.margin = "10px 0";
                errorDiv.style.display = "none";
                form.prepend(errorDiv);
                console.log("🛠️ Error container added");
            }

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
                console.log(`📝 Default type set to: ${defaultType}`);
            }

            form.addEventListener("submit", e => {
                e.preventDefault();
                const data = new FormData(form);
                const postUrl = txId ? `/transaction/edit/${txId}/` : "/transaction/";

                const errorContainer = document.getElementById("formError");
                if (errorContainer) errorContainer.style.display = "none";

                console.log("📤 Submitting transaction form to:", postUrl);

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
                        console.log("✅ Transaction saved:", res.transaction);
                        updateTransactionList(res.transaction);
                        updateTopSummary(res);

                        // Update budgetsData if backend returns budget info
                        if (res.budget) {
                            window.budgetsData = window.budgetsData || {};
                            window.budgetsData[res.budget.category_id] = res.budget;
                        }

                        // Dispatch event
                        const catId = res.transaction.category_id || res.transaction.category;
                        if (catId) {
                            window.dispatchEvent(new CustomEvent("transaction:changed", {
                                detail: {
                                    transaction: {
                                        category_id: String(catId),
                                        amount: parseFloat(res.transaction.amount),
                                        type: (res.transaction.type || "expense").toLowerCase()
                                    },
                                    action: txId ? "edit" : "add"
                                }
                            }));
                        }

                        setTimeout(() => closeModal(), 1000);

                    } else if (res.error === "login_required") {
                        console.warn("⚠️ Login required, redirecting...");
                        window.location.href = "/userauths/login/";
                    } else {
                        if (errorContainer) {
                            errorContainer.textContent = res.error || "Failed to save transaction.";
                            errorContainer.style.display = "block";
                            setTimeout(() => { errorContainer.style.display = "none"; }, 5000);
                        }
                    }
                })
                .catch(err => {
                    if (errorContainer) {
                        errorContainer.textContent = "Network error. Please try again.";
                        errorContainer.style.display = "block";
                        setTimeout(() => { errorContainer.style.display = "none"; }, 5000);
                    }
                    console.error("❌ Error submitting transaction:", err);
                });
            });
        })
        .catch(err => console.error("❌ Failed to load modal:", err));
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
            }

            updateTopSummary(res);

            // Update budgetsData if backend returns budget info
            if (res.budget) {
                window.budgetsData = window.budgetsData || {};
                window.budgetsData[res.budget.category_id] = res.budget;
            }

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

// -------------------------------
// 🔔 Budget Alert: show alert if exceeded
// -------------------------------
window.addEventListener("transaction:changed", e => {
    const { transaction } = e.detail;

    if (!window.budgetsData) return;

    const budget = window.budgetsData[transaction.category_id];
    if (!budget) return;

    // ✅ budget.spent already updated from backend (res.budget)
    showBudgetAlert(budget, transaction.category_id);

});
window.shownBudgetAlerts = new Set();

function showBudgetAlert(budget, categoryId) {
    if (!budget.budget || budget.budget <= 0) return; // 🛡️ safety

    const percent = (budget.spent / budget.budget) * 100;

    // 🧹 RESET alerts if budget drops below 90%
    if (percent < 90) {
        window.shownBudgetAlerts.delete(`${categoryId}-warn`);
        window.shownBudgetAlerts.delete(`${categoryId}-full`);
        return;
    }

    const key = `${categoryId}-${percent >= 100 ? "full" : "warn"}`;

    // 🚫 prevent duplicate alerts
    if (window.shownBudgetAlerts.has(key)) return;

    if (percent >= 100) {
        alert(`🚨 Budget limit reached for "${budget.name}"`);
    } else if (percent >= 90) {
        alert(`⚠️ "${budget.name}" budget is about to reach its limit`);
    }

    window.shownBudgetAlerts.add(key);
}
