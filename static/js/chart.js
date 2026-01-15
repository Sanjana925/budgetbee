document.addEventListener("DOMContentLoaded", () => {
    const ctx = document.getElementById('chartCanvas');
    const emptyText = document.getElementById('chartEmpty');
    const tbody = document.getElementById('monthlyTotalsBody');
    if (!ctx || !tbody || !emptyText) return;

    let chart = null;

    // ----------------- Toggle Buttons -----------------
    const toggleBtns = document.querySelectorAll('.toggle .toggle-btn');

    // ----------------- Default type -----------------
    let currentType = typeof category_type !== 'undefined' ? category_type : 'expense';

    // ----------------- Set active toggle -----------------
    toggleBtns.forEach(btn => {
        if (btn.dataset.type === currentType) btn.classList.add('active');
        else btn.classList.remove('active');
    });

    // ----------------- Toggle click -----------------
    toggleBtns.forEach(btn => {
        btn.addEventListener('click', e => {
            e.preventDefault();

            // Remove active from all, add to clicked
            toggleBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            currentType = btn.dataset.type;
            renderChart(currentType);
        });
    });

    // ----------------- Render Chart -----------------
    function renderChart(type) {
        if (chart) chart.destroy();

        const dataObj = type === 'expense' ? expenseData : incomeData;
        const labels = Object.keys(dataObj);
        const values = Object.values(dataObj);

        // Show empty message if no data
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
                plugins: {
                    legend: { position: 'right', labels: { boxWidth: 20, padding: 15 } },
                    tooltip: { callbacks: { label: ctx => `${ctx.label}: ${ctx.parsed}` } }
                },
                cutout: '70%'
            },
            plugins: [{
                id: 'centerText',
                beforeDraw: chart => {
                    const { ctx, width, height } = chart;
                    ctx.restore();
                    const fontSize = (height / 114).toFixed(2);
                    ctx.font = "bold " + fontSize + "em Arial";
                    ctx.textBaseline = "middle";
                    const text = type === 'expense' ? "Expenses" : "Income";
                    const textX = Math.round((width - ctx.measureText(text).width) / 2);
                    const textY = height / 2;
                    ctx.fillText(text, textX, textY);
                    ctx.save();
                }
            }]
        });

        updateMonthlyTable(type);
    }

    // ----------------- Monthly Table -----------------
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

    // ----------------- Initial render -----------------
    renderChart(currentType);
});
