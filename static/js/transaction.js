document.addEventListener("DOMContentLoaded", function() {
    const btn = document.getElementById("newTransactionBtn");

    btn.onclick = function() {
        openModal();
    };
});

function openModal() {
    if (document.getElementById("transactionModal")) return;

    fetch("/transaction-modal/")
        .then(res => res.text())
        .then(html => {
            document.body.insertAdjacentHTML("beforeend", html);
            document.body.classList.add("modal-open");

            const form = document.getElementById("transactionForm");
            form.addEventListener("submit", function(e) {
                e.preventDefault();
                const data = new FormData(form);

                fetch("/transaction/add/", {
                    method: "POST",
                    body: data,
                    headers: { "X-Requested-With": "XMLHttpRequest" }
                })
                .then(res => res.json())
                .then(res => {
                    if (res.success) {
                        // Update Home summary
                        const amounts = document.querySelectorAll(".summary-left .amount");
                        amounts[0].innerText = "Rs. " + res.total_income.toFixed(2);
                        amounts[1].innerText = "Rs. " + res.total_expense.toFixed(2);
                        document.querySelector(".summary-right .balance-amount").innerText = "Rs. " + res.balance.toFixed(2);

                        closeModal();
                    } else if (res.error === "login_required") {
                        window.location.href = "/userauths/login/";
                    }
                });
            });
        });
}

function closeModal() {
    const modal = document.getElementById("transactionModal");
    if (modal) modal.remove();
    document.body.classList.remove("modal-open");
}
