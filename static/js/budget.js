document.addEventListener("DOMContentLoaded", () => {
    const budgetPopup = document.getElementById("budgetPopup");
    const openAddBtn = document.getElementById("openAddBudget");
    const cancelBudgetBtn = document.getElementById("cancelBudget");
    const budgetForm = document.getElementById("budgetForm");
    const budgetList = document.querySelector(".budget-list");
    const budgetsDataEl = document.getElementById("budgetsData");
    const budgetsData = budgetsDataEl ? JSON.parse(budgetsDataEl.textContent) : {};

    let editingCategoryId = null;

    function getCSRFToken() {
        const name = "csrftoken";
        const cookies = document.cookie.split(";").map(c => c.trim());
        for (let c of cookies) if (c.startsWith(name + "=")) return decodeURIComponent(c.slice(name.length + 1));
        return null;
    }

    openAddBtn?.addEventListener("click", () => {
        editingCategoryId = null;
        budgetPopup.classList.remove("hidden");
        document.getElementById("popupTitle").textContent = "Set Budget";
        budgetForm.reset();
    });

    cancelBudgetBtn?.addEventListener("click", () => budgetPopup.classList.add("hidden"));

    budgetList.querySelectorAll(".edit-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            editingCategoryId = String(btn.dataset.id);
            const data = budgetsData[editingCategoryId];
            if (!data) return;

            budgetPopup.classList.remove("hidden");
            document.getElementById("popupTitle").textContent = "Edit Budget";
            budgetForm.category.value = editingCategoryId;
            budgetForm.amount.value = data.budget || 0;
        });
    });

    function updateBudgetCard(catId, data) {
        catId = String(catId);
        const card = budgetList.querySelector(`.budget-card[data-id='${catId}']`);
        if (!card) return;

        const spent = parseFloat(data.spent || 0);
        const budget = parseFloat(data.budget || 0);
        const percent = budget > 0 ? Math.min(Math.round((spent / budget) * 100), 100) : 0;
        const exceeded = budget > 0 && spent >= budget;

        card.querySelector(".spent").textContent = spent.toFixed(2);
        card.querySelector(".budget-amount").textContent = budget.toFixed(2);

        const progress = card.querySelector(".budget-progress");
        if (progress) progress.style.width = `${percent}%`;
        if (progress) progress.style.background = exceeded ? "#e53935" : "#4caf50";

        card.classList.toggle("budget-exceeded", exceeded);

        budgetsData[catId] = {
            spent, budget, percent,
            name: data.name || budgetsData[catId]?.name || "",
            icon: data.icon || budgetsData[catId]?.icon || ""
        };
    }

    function fetchBudgetSpent(catId) {
        catId = String(catId);
        const [monthStr, yearStr] = document.querySelector(".month-nav span").textContent.split("/");

        const data = new FormData();
        data.append("category", parseInt(catId, 10));
        data.append("month", parseInt(monthStr, 10));
        data.append("year", parseInt(yearStr, 10));

        fetch(getBudgetSpentUrl, {
            method: "POST",
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": getCSRFToken()
            },
            body: data
        })
        .then(res => res.json())
        .then(data => { if (data.success) updateBudgetCard(catId, data); })
        .catch(err => console.error("Failed to refresh budget spent:", err));
    }

    budgetForm?.addEventListener("submit", e => {
        e.preventDefault();
        const formData = new FormData(budgetForm);
        const [monthStr, yearStr] = document.querySelector(".month-nav span").textContent.split("/");
        formData.append("month", parseInt(monthStr, 10));
        formData.append("year", parseInt(yearStr, 10));

        fetch(saveBudgetUrl, {
            method: "POST",
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": formData.get("csrfmiddlewaretoken") || getCSRFToken()
            },
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                updateBudgetCard(formData.get("category"), data);
                budgetPopup.classList.add("hidden");
            } else alert(data.error || "Failed to save budget.");
        })
        .catch(err => console.error("Budget save error:", err));
    });

    // Listen for transaction changes to refresh budgets
    window.addEventListener("transaction:changed", e => {
        const tx = e.detail.transaction;
        if (!tx) return;

        const catId = tx.category_id || tx.category;
        const txType = (tx.type || "").toLowerCase();
        if (!catId || txType !== "expense") return;

        fetchBudgetSpent(catId);
    });

    // Initialize all budget cards
    Object.keys(budgetsData).forEach(catId => updateBudgetCard(catId, budgetsData[catId]));
});
