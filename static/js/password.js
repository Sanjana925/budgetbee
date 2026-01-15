document.addEventListener("DOMContentLoaded", function () {

    // Get modal and buttons
    const modal = document.getElementById('password-modal');
    const btn = document.getElementById('open-password-modal');
    const closeBtn = document.querySelector('.modal .close');

    // Open modal
    btn.onclick = () => {
        modal.style.display = 'block';
    };

    // Close modal
    closeBtn.onclick = () => {
        modal.style.display = 'none';
    };

    // Close modal when clicking outside content
    window.onclick = (event) => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    };

});
