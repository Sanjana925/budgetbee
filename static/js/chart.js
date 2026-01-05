const ctx = document.getElementById('chartCanvas');
let chart;

// Category colors from backend
const categoryColors = JSON.parse('{{ category_colors_json|escapejs }}');

function renderChart(type) {
    if (chart) chart.destroy();

    const dataObj = type === 'expense' ? expenseData : incomeData;
    const labels = Object.keys(dataObj);
    const values = Object.values(dataObj);

    if (!values.length) {
        document.getElementById('chartEmpty').style.display = "block";
        return;
    } else {
        document.getElementById('chartEmpty').style.display = "none";
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
                tooltip: {
                    callbacks: { label: ctx => `${ctx.label}: ${ctx.parsed}` }
                }
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

    populateMonthlyTable(type);
}

// ---------------- Monthly Table ----------------
function populateMonthlyTable(type) {
    const tbody = document.getElementById('monthlyTotalsBody');
    tbody.innerHTML = "";

    const dataObj = type === 'expense' ? expenseData : incomeData;
    const labels = Object.keys(dataObj);

    monthlyData.forEach(item => {
        const balance = item.income - item.expense;

        // Color legend for active categories
        const colorCells = labels.map(l => 
            `<span style="display:inline-block;width:12px;height:12px;background:${categoryColors[l]};margin-right:6px;border-radius:3px;"></span>${l}`
        ).join('<br>');

        const row = `<tr>
            <td>${colorCells}</td>
            <td>${item.date}</td>
            <td>${item.expense.toLocaleString()}</td>
            <td>${item.income.toLocaleString()}</td>
            <td>${balance.toLocaleString()}</td>
        </tr>`;
        tbody.innerHTML += row;
    });
}

// Initial chart
renderChart('expense');
