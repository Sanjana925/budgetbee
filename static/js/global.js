document.addEventListener("DOMContentLoaded", function () {

    console.log("✅ global.js loaded");

    // Check authentication from body dataset
    const isAuthenticated = document.body.dataset.auth === "true";
    console.log("🔐 isAuthenticated:", isAuthenticated);

    // Elements that require authentication
    const authElements = document.querySelectorAll("[data-requires-auth]");
    console.log("🔎 data-requires-auth elements found:", authElements.length);

    // Attach click handlers to auth elements
    authElements.forEach(el => {
        console.log("➕ auth element:", el);

        el.addEventListener("click", function (e) {
            console.log("🖱️ auth element clicked");

            if (!isAuthenticated) {
                e.preventDefault();

                const modal = document.getElementById("loginRequiredModal");
                console.log("📦 loginRequiredModal found:", modal);

                if (modal) {
                    modal.classList.remove("hidden"); // show login popup
                    console.log("👀 popup shown");
                } else {
                    console.log("❌ popup NOT found");
                }
            }
        });
    });

    // Close button inside login popup
    const closeBtn = document.getElementById("closeLoginModal");
    console.log("❎ closeLoginModal found:", closeBtn);

    if (closeBtn) {
        closeBtn.addEventListener("click", function () {
            const modal = document.getElementById("loginRequiredModal");
            if (modal) modal.classList.add("hidden"); // hide popup
        });
    }

    // Clicking outside popup card closes it
    const modal = document.getElementById("loginRequiredModal");
    console.log("📦 modal container:", modal);

    if (modal) {
        modal.addEventListener("click", function (e) {
            if (e.target === modal) modal.classList.add("hidden");
        });
    }

});
