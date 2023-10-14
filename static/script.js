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
            createChart(parsedData);
        }
    });
}


function createChart(data) {
    const ctx = document.getElementById('rwChart').getContext('2d');
    
    if (rwChartInstance) {
        rwChartInstance.destroy();
    }

    rwChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.RW_X,
            datasets: [{
                label: 'RW Data',
                data: data.RW_Y,
                borderColor: 'rgba(75, 192, 192, 1)',
                fill: false
            }]
        },
        options: {
            scales: {
                x: {
                    beginAtZero: true
                },
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}
