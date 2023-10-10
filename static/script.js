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
            document.getElementById('text').innerText = data.data;
            const parsedData = JSON.parse(data.data);
            createChart(parsedData);
        }
    });
}

function createChart(data) {
    const ctx = document.getElementById('rwChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: Array.from({length: data.RW.length}, (_, i) => i + 1),
            datasets: [{
                label: 'RW Data',
                data: data.RW,
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
