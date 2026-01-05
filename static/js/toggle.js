// finance/js/toggle.js
// Toggle buttons for charts
document.getElementById('expenseBtn').onclick = () => {
    setActive('expenseBtn');
    renderChart('expense');
};

document.getElementById('incomeBtn').onclick = () => {
    setActive('incomeBtn');
    renderChart('income');
};

// Set active button styling
function setActive(id) {
    document.querySelectorAll('.toggle button').forEach(b => b.classList.remove('active'));
    document.getElementById(id).classList.add('active');
}
