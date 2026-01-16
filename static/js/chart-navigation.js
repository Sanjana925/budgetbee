/* chart-navigation.js */
document.addEventListener("DOMContentLoaded", () => {

    const prevBtn = document.getElementById("prevMonthBtn");
    const nextBtn = document.getElementById("nextMonthBtn");
    const monthLabel = document.getElementById("currentMonthLabel");

    let currentYear = parseInt(monthLabel.dataset.year);
    let currentMonth = parseInt(monthLabel.dataset.month);

    function updateMonthLabel() {
        const date = new Date(currentYear, currentMonth - 1);
        monthLabel.textContent = date.toLocaleString('default', { month: 'short', year: 'numeric' });
    }

    function reloadChartAndTable() {
        const filteredMonthly = [];
        const filteredIncome = {};
        const filteredExpense = {};

        monthlyDataAll.forEach(item => {
            const itemDate = new Date(item.date);
            if(itemDate.getFullYear() === currentYear && (itemDate.getMonth()+1) === currentMonth) {
                filteredMonthly.push(item);

                for(const [cat, val] of Object.entries(incomeDataAll[item.date] || {})) {
                    filteredIncome[cat] = (filteredIncome[cat] || 0) + val;
                }
                for(const [cat, val] of Object.entries(expenseDataAll[item.date] || {})) {
                    filteredExpense[cat] = (filteredExpense[cat] || 0) + val;
                }
            }
        });

        // Update global vars for chart.js
        window.incomeData = filteredIncome;
        window.expenseData = filteredExpense;
        window.monthlyData = filteredMonthly;

        // Re-render chart
        const activeTypeBtn = document.querySelector('.toggle-btn.active');
        const type = activeTypeBtn ? activeTypeBtn.dataset.type : 'expense';
        renderChart(type);
    }

    prevBtn.addEventListener("click", () => {
        currentMonth--;
        if(currentMonth < 1) { currentMonth = 12; currentYear--; }
        updateMonthLabel();
        reloadChartAndTable();
    });

    nextBtn.addEventListener("click", () => {
        currentMonth++;
        if(currentMonth > 12) { currentMonth = 1; currentYear++; }
        updateMonthLabel();
        reloadChartAndTable();
    });

    // Initial label & data load
    updateMonthLabel();
    reloadChartAndTable();
});
