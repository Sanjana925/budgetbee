document.addEventListener("DOMContentLoaded", function () {

    const isAuthenticated = document.body.dataset.auth === "true";

    // All buttons or links that require login
    document.querySelectorAll("[data-requires-auth]").forEach(el => {
        el.addEventListener("click", function (e) {
            if (!isAuthenticated) {
                e.preventDefault();
                const modal = document.getElementById("loginRequiredModal");
                if (modal) modal.classList.remove("hidden"); // show popup
            }
        });
    });

    // Close button inside popup
    const closeBtn = document.getElementById("closeLoginModal");
    if (closeBtn) {
        closeBtn.addEventListener("click", function () {
            const modal = document.getElementById("loginRequiredModal");
            if (modal) modal.classList.add("hidden"); // hide popup
        });
    }

    // Clicking outside popup card closes it
    const modal = document.getElementById("loginRequiredModal");
    if (modal) {
        modal.addEventListener("click", function (e) {
            if (e.target === modal) {
                modal.classList.add("hidden"); // hide popup
            }
        });
    }

});
