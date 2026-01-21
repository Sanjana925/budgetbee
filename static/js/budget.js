console.log("📦 budget.js loaded");

document.addEventListener("DOMContentLoaded", () => {
    console.log("✅ DOM fully loaded");

    const budgetPopup = document.getElementById("budgetPopup");
    const openAddBtn = document.getElementById("openAddBudget");
    const cancelBudgetBtn = document.getElementById("cancelBudget");
    const budgetForm = document.getElementById("budgetForm");
    const budgetList = document.querySelector(".budget-list");
    const budgetsDataEl = document.getElementById("budgetsData");
    let budgetsData = budgetsDataEl ? JSON.parse(budgetsDataEl.textContent) : {};

    const container = document.getElementById("budgetContainer");
    const getBudgetSpentUrl = container.dataset.getBudgetSpentUrl;
    const saveBudgetUrl = container.dataset.saveBudgetUrl;

    console.log("🔗 Budget URLs:", getBudgetSpentUrl, saveBudgetUrl);

    let editingCategoryId = null;

    function getCSRFToken() {
        const name = "csrftoken";
        const cookies = document.cookie.split(";").map(c => c.trim());
        for (let c of cookies) if (c.startsWith(name + "=")) return decodeURIComponent(c.slice(name.length + 1));
        return null;
    }

    // -------------------
    // Safe month/year getter
    // -------------------
    function getCurrentMonthYear() {
        const monthSpan = document.querySelector(".month-nav span");
        let month = 1, year = 2026; // fallback
        if (monthSpan?.textContent) {
            const parts = monthSpan.textContent.trim().split("/");
            if (parts.length === 2) {
                const m = parseInt(parts[0], 10);
                const y = parseInt(parts[1], 10);
                if (!isNaN(m) && !isNaN(y)) {
                    month = m;
                    year = y;
                }
            }
        }
        return { month, year };
    }

    // -------------------
    // Animate numbers
    // -------------------
    function animateNumber(element, start, end, duration = 500) {
        start = parseFloat(start) || 0;
        end = parseFloat(end) || 0;
        const range = end - start;
        if (range === 0) {
            element.textContent = end.toFixed(2);
            return;
        }
        const startTime = performance.now();
        function step(timestamp) {
            const progress = Math.min((timestamp - startTime) / duration, 1);
            const value = start + range * progress;
            element.textContent = value.toFixed(2);
            if (progress < 1) requestAnimationFrame(step);
        }
        requestAnimationFrame(step);
    }

    // -------------------
    // Open Add Budget
    // -------------------
    openAddBtn?.addEventListener("click", () => {
        editingCategoryId = null;
        budgetPopup?.classList.remove("hidden");
        document.getElementById("popupTitle").textContent = "Set Budget";
        budgetForm.reset();
        console.log("📝 Open Add Budget popup");
    });

    // -------------------
    // Cancel Budget
    // -------------------
    cancelBudgetBtn?.addEventListener("click", () => {
        budgetPopup?.classList.add("hidden");
        console.log("❌ Closed Budget popup");
    });

    // -------------------
    // Edit Budget buttons
    // -------------------
    function initEditButtons() {
        budgetList?.querySelectorAll(".edit-btn").forEach(btn => {
            btn.addEventListener("click", () => {
                editingCategoryId = String(btn.dataset.id);
                const data = budgetsData[editingCategoryId];
                if (!data) return;

                budgetPopup.classList.remove("hidden");
                document.getElementById("popupTitle").textContent = "Edit Budget";
                budgetForm.category.value = editingCategoryId;
                budgetForm.amount.value = data.budget || 0;
                console.log("✏️ Editing budget for category", editingCategoryId);
            });
        });
    }

    initEditButtons();

    // -------------------
    // Update budget card
    // -------------------
    function updateBudgetCard(catId, data) {
        catId = String(catId);
        const card = budgetList.querySelector(`.budget-card[data-id='${catId}']`);
        if (!card) return;

        const spent = parseFloat(data.spent || 0);
        const budget = parseFloat(data.budget || 0);
        const percent = budget > 0 ? Math.min(Math.round((spent / budget) * 100), 100) : 0;
        const exceeded = budget > 0 && spent >= budget;

        animateNumber(card.querySelector(".spent"), parseFloat(card.querySelector(".spent").textContent || 0), spent);
        animateNumber(card.querySelector(".budget-amount"), parseFloat(card.querySelector(".budget-amount").textContent || 0), budget);

        const progress = card.querySelector(".budget-progress");
        if (progress) {
            progress.style.width = `${percent}%`;
            progress.style.background = exceeded ? "#e53935" : "#4caf50";
        }

        card.classList.toggle("budget-exceeded", exceeded);

        budgetsData[catId] = {
            spent,
            budget,
            percent,
            name: data.name || budgetsData[catId]?.name || "",
            icon: data.icon || budgetsData[catId]?.icon || ""
        };

        console.log("🔄 Budget card updated", catId, budgetsData[catId]);
    }

    // -------------------
    // Fetch single category budget spent
    // -------------------
    function fetchBudgetSpent(catId) {
        catId = String(catId);
        const { month, year } = getCurrentMonthYear();

        if (!catId || !month || !year) {
            console.warn("⚠️ Invalid category/month/year for fetchBudgetSpent", catId, month, year);
            return Promise.resolve();
        }

        const data = new FormData();
        data.append("category", parseInt(catId, 10));
        data.append("month", month);
        data.append("year", year);

        return fetch(getBudgetSpentUrl, {
            method: "POST",
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": getCSRFToken()
            },
            body: data
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) updateBudgetCard(catId, data);
            else console.warn("⚠️ Failed to fetch budget spent", data);
        })
        .catch(err => console.error("❌ Fetch budget error:", err));
    }

    // -------------------
    // Fetch all budgets
    // -------------------
    function fetchAllBudgets() {
        if (!budgetList) return;
        Array.from(budgetList.querySelectorAll(".budget-card")).forEach(c => fetchBudgetSpent(c.dataset.id));
        console.log("📊 All budgets fetched from server");
    }

    // -------------------
    // Form submit (Save Budget)
    // -------------------
    budgetForm?.addEventListener("submit", e => {
        e.preventDefault();
        const formData = new FormData(budgetForm);
        const { month, year } = getCurrentMonthYear();
        formData.append("month", month);
        formData.append("year", year);

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
                console.log("✅ Budget saved", data);
            } else {
                alert(data.error || "Failed to save budget.");
                console.warn("⚠️ Budget save failed", data);
            }
        })
        .catch(err => console.error("❌ Budget save error:", err));
    });

    // -------------------
    // Listen to transaction changes
    // -------------------
    window.addEventListener("transaction:changed", e => {
        const tx = e.detail.transaction;
        if (!tx) return;

        const catId = String(tx.category_id || tx.category);
        const txType = (tx.type || "").toLowerCase();
        if (!catId || txType !== "expense") return;

        setTimeout(() => fetchBudgetSpent(catId), 200);
        console.log("💰 Transaction changed, updating category", catId);
    });

    // -------------------
    // Month navigation AJAX
    // -------------------
    document.querySelectorAll(".month-nav a").forEach(link => {
        link.addEventListener("click", e => {
            e.preventDefault();
            const url = link.getAttribute("href");
            if (!url) return;

            fetch(url, { headers: { "X-Requested-With": "XMLHttpRequest" } })
                .then(res => res.text())
                .then(html => {
                    const parser = new DOMParser();
                    const doc = parser.parseFromString(html, "text/html");
                    const newBudgetList = doc.querySelector(".budget-list");
                    const newMonthSpan = doc.querySelector(".month-nav span");
                    if (newBudgetList) budgetList.innerHTML = newBudgetList.innerHTML;
                    if (newMonthSpan) document.querySelector(".month-nav span").textContent = newMonthSpan.textContent;

                    initEditButtons();

                    const newBudgetsDataEl = doc.getElementById("budgetsData");
                    if (newBudgetsDataEl) budgetsData = JSON.parse(newBudgetsDataEl.textContent);

                    fetchAllBudgets();
                    console.log("📅 Month navigation loaded via AJAX");
                })
                .catch(err => console.error("❌ Failed to load month:", err));
        });
    });

    // -------------------
    // Initialize page
    // -------------------
    Object.keys(budgetsData).forEach(catId => updateBudgetCard(catId, budgetsData[catId]));
    fetchAllBudgets();

    console.log("📦 Budget initialization complete");
});
