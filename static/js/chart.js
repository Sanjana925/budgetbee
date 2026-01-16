
/* Charts rendering and monthly table update */
document.addEventListener("DOMContentLoaded", () => {
    const ctx = document.getElementById('chartCanvas');
    const emptyText = document.getElementById('chartEmpty');
    const tbody = document.getElementById('monthlyTotalsBody');
    if (!ctx || !tbody || !emptyText) return;

    let chart = null;
    const toggleBtns = document.querySelectorAll('.toggle .toggle-btn');
    let currentType = typeof category_type !== 'undefined' ? category_type : 'expense';

    toggleBtns.forEach(btn => {
        if (btn.dataset.type === currentType) btn.classList.add('active');
        else btn.classList.remove('active');
    });

    toggleBtns.forEach(btn => {
        btn.addEventListener('click', e => {
            e.preventDefault();
            toggleBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentType = btn.dataset.type;
            renderChart(currentType);
        });
    });

    function renderChart(type) {
        if (chart) chart.destroy();

        const dataObj = type === 'expense' ? expenseData : incomeData;
        const labels = Object.keys(dataObj);
        const values = Object.values(dataObj);

        if (!values.length || values.reduce((a, b) => a + b, 0) === 0) {
            emptyText.style.display = "block";
            ctx.style.display = "none";
            updateMonthlyTable(type);
            return;
        } else {
            emptyText.style.display = "none";
            ctx.style.display = "block";
        }

        chart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels.length ? labels : ['No data'],
                datasets: [{
                    data: values.length ? values : [1],
                    backgroundColor: labels.length ? labels.map(l => categoryColors[l] || '#ddd') : ['#ddd'],
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: { boxWidth: 20, padding: 10, font: { size: 12 } }
                    },
                    tooltip: { callbacks: { label: ctx => `${ctx.label}: ${ctx.parsed}` } }
                },
                cutout: '60%'
            }
        });

        updateMonthlyTable(type);
    }

    function updateMonthlyTable(type) {
        tbody.innerHTML = "";
        monthlyData.forEach(item => {
            const balance = item.income - item.expense;
            const row = `<tr>
                <td>${item.date}</td>
                <td>${item.expense.toLocaleString()}</td>
                <td>${item.income.toLocaleString()}</td>
                <td style="color:${balance >= 0 ? 'green' : 'red'}">${balance.toLocaleString()}</td>
            </tr>`;
            tbody.innerHTML += row;
        });
    }

    renderChart(currentType);
});


