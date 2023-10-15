let rwChartInstance = null;

function getData() {
    const uid = document.getElementById('uid').value;
    fetch('/get_data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({uid: uid})
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
        } else {
            const parsedData = JSON.parse(data.data);
            
            // Отображение даты и времени
            document.getElementById('text').innerText = parsedData.date;

            // Отображение данных из словаря pg
            const pgDataDiv = document.getElementById('pgData');
            pgDataDiv.innerHTML = '';  // очистка предыдущих данных
            for (const [key, value] of Object.entries(parsedData.PG || {})) {
                pgDataDiv.innerHTML += `<strong>${key}:</strong> ${value}<br>`;
            }

            // Обновление графика
            updateChart(parsedData);
        }
    });
}

function updateChart(data) {
    if (window.myChart) {
        window.myChart.destroy();
    }

    const ctx = document.getElementById('rwChart').getContext('2d');
    window.myChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [...new Set([...data.RW_X, ...data.PG_X])].sort((a, b) => a - b),
            datasets: [
                {
                    label: 'RW Data',
                    data: data.RW_X.map((x, i) => ({x: x, y: data.RW_Y[i]})),
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1,
                    fill: false,
                    yAxisID: 'y-axis-1'  // Используем первую ось Y для RW Data
                },
                {
                    label: 'PG Data',
                    data: data.PG_X.map((x, i) => ({x: x, y: data.PG_Y[i]})),
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 1,
                    fill: false,
                    yAxisID: 'y-axis-2'  // Используем вторую ось Y для PG Data
                }
            ]
        },
        options: {
            scales: {
                x: { beginAtZero: true },
                'y-axis-1': {
                    beginAtZero: true,
                    position: 'left'
                },
                'y-axis-2': {
                    min: 30,
                    max: 90,
                    position: 'right'
                }
            }
        }
    });
}
