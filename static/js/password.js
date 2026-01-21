// Password modal handling
document.addEventListener("DOMContentLoaded", function() {
    const modal = document.getElementById("password-modal");
    const btn = document.getElementById("open-password-modal");
    const span = document.querySelector(".close");

    // Open modal
    btn.onclick = function() {
        modal.style.display = "block";
    }

    // Close modal
    span.onclick = function() {
        modal.style.display = "none";
    }

    // Close modal if clicked outside
    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }
});

// Auto-hide messages after 3 seconds
document.addEventListener("DOMContentLoaded", function() {
    const messages = document.querySelectorAll(".messages li");
    if (messages.length > 0) {
        setTimeout(() => {
            messages.forEach(msg => {
                msg.style.transition = "opacity 0.5s, transform 0.5s";
                msg.style.opacity = "0";
                msg.style.transform = "translateY(-10px)";
                // Remove from DOM after fade out
                setTimeout(() => msg.remove(), 500);
            });
        }, 3000); // 3 seconds
    }
});
