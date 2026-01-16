document.addEventListener("DOMContentLoaded", () => {

    const ctx = document.getElementById('chartCanvas');
    const emptyText = document.getElementById('chartEmpty');
    const tbody = document.getElementById('monthlyTotalsBody');
    const prevBtn = document.getElementById("prevMonthBtn");
    const nextBtn = document.getElementById("nextMonthBtn");
    const monthLabel = document.getElementById("currentMonthLabel");
    const toggleBtns = document.querySelectorAll('.toggle-btn');

    let chart = null;
    let currentType = 'expense';

    function updateMonthLabel() {
        const date = new Date(window.currentYear, window.currentMonth - 1);
        monthLabel.textContent = date.toLocaleString('default', { month: 'short', year: 'numeric' });
    }

    function renderChart(type) {
        if (chart) chart.destroy();

        const dataObj = type === 'expense' ? window.expenseDataAll : window.incomeDataAll;
        const labels = Object.keys(dataObj);
        const values = Object.values(dataObj);

        if (!values.length || values.reduce((a, b) => a + b, 0) === 0) {
            emptyText.style.display = "block";
            ctx.style.display = "none";
        } else {
            emptyText.style.display = "none";
            ctx.style.display = "block";

            chart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: labels.length ? labels : ['No data'],
                    datasets: [{
                        data: values.length ? values : [1],
                        backgroundColor: labels.length
                            ? labels.map(l => window.categoryColors[l] || '#ddd')
                            : ['#ddd']
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
                        tooltip: {
                            callbacks: {
                                label: ctx => `${ctx.label}: Rs. ${ctx.parsed}`
                            }
                        }
                    },
                    cutout: '60%'
                }
            });
        }

        updateMonthlyTable();
    }

    function updateMonthlyTable() {
        tbody.innerHTML = "";
        window.monthlyDataAll.forEach(item => {
            const balance = item.income - item.expense;
            tbody.innerHTML += `
                <tr>
                    <td>${item.date}</td>
                    <td>${item.expense.toLocaleString()}</td>
                    <td>${item.income.toLocaleString()}</td>
                    <td style="color:${balance >= 0 ? 'green' : 'red'}">
                        ${balance.toLocaleString()}
                    </td>
                </tr>`;
        });
    }

    toggleBtns.forEach(btn => {
        btn.addEventListener('click', e => {
            e.preventDefault();
            toggleBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentType = btn.dataset.type;
            renderChart(currentType);
        });
    });

    function changeMonth(delta) {
        let newMonth = window.currentMonth + delta;
        let newYear = window.currentYear;

        if (newMonth < 1) { newMonth = 12; newYear--; }
        if (newMonth > 12) { newMonth = 1; newYear++; }

        window.location.href = `/chart/${newYear}/${newMonth}/`;
    }

    prevBtn.addEventListener('click', () => changeMonth(-1));
    nextBtn.addEventListener('click', () => changeMonth(1));

    updateMonthLabel();
    renderChart(currentType);

    toggleBtns.forEach(btn => {
        if (btn.dataset.type === currentType) btn.classList.add('active');
    });

});
