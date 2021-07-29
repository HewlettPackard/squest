function createPieChart(data, id) {

    var config = {
        type: 'pie',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,

        }
    };

    var ctx = document.getElementById(id).getContext('2d');
    window.myPie = new Chart(ctx, config);
}
