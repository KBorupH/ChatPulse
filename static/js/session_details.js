const canvas = document.getElementById("per-minute-chart");
const perMinute = JSON.parse(canvas.dataset.points);

new Chart(canvas, {
    type: "line",
    data: {
        labels: perMinute.map((p) => new Date(p.minute).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit"})),
        datasets: [{
            label: "Messages",
            data: perMinute.map((p) => p.count),
        }],
    },
    options: {
        elements: {
            line: {
                tension: 0.4,
                borderColor: "#1A80E0",
            },
            point: {
                radius: 0,
                hoverRadius: 4,
                backgroundColor: "#0b507e9a"
            }
        },
        interaction: {
            mode: "index",
            intersect: false,
        },
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
            x: {
                grid: { color: "rgba(121, 117, 117, 0.2)" },
                ticks: { color: "#dee2e6", maxTicksLimit: 30 },
            }, 
            y: { 
                beginAtZero: true,
                grid: { color: "rgba(163, 156, 156, 0.2)" },
                ticks: { color: "#dee2e6", precision: 0 },
            },
        },
    },
});