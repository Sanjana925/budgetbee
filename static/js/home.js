// Home page month navigation
document.addEventListener("DOMContentLoaded", () => {
    const prevBtn = document.getElementById("prevMonthBtn");
    const nextBtn = document.getElementById("nextMonthBtn");
    const monthLabel = document.getElementById("currentMonthLabel");

    // Current year & month from HTML
    let currentYear = parseInt(monthLabel.dataset.year);
    let currentMonth = parseInt(monthLabel.dataset.month); // 1-12

    // Update the month label text
    function updateMonthLabel() {
        const dateObj = new Date(currentYear, currentMonth - 1); // JS months: 0-11
        monthLabel.textContent = dateObj.toLocaleString('default', { month: 'short', year: 'numeric' });
    }

    // Navigate months forward/back
    function navigateMonth(delta) {
        currentMonth += delta;
        if (currentMonth < 1) {
            currentMonth = 12;
            currentYear -= 1;
        } else if (currentMonth > 12) {
            currentMonth = 1;
            currentYear += 1;
        }

        updateMonthLabel();

        // Redirect to Django view for selected month
        window.location.href = `/${currentYear}/${currentMonth}/`;
    }

    prevBtn.addEventListener("click", () => navigateMonth(-1));
    nextBtn.addEventListener("click", () => navigateMonth(1));

    updateMonthLabel();
});
