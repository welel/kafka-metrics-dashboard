const API_URL = api_base_url || 'http://localhost:8000';

LABELS = {
    'db_service': 'DB Service',
}

var tasksLineCharts = {};
var speedsLineCharts = {};
var progressPieCharts = {};


function formatToK(number) {
    let k_num = 0;
    while (number >= 1000) {
        number = number / 1000;
        k_num += 1;
    }
    number = number.toFixed(0);
    return number + 'k'.repeat(k_num)
}

function getNumberWithCommas(number) {
    return number.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

function formatSecondsToTimeLeft(seconds) {
    let date = new Date(seconds * 1000);
    months = date.getUTCMonth();
    days = date.getUTCDate() - 1;
    hours = date.getUTCHours().toString().padStart(2, '0');
    minutes = date.getUTCMinutes().toString().padStart(2, '0');
    seconds = date.getUTCSeconds().toString().padStart(2, '0');

    let days_count = 0;
    date = '';
    if (months) {
        days_count = months * 30;
    }
    if (days) {
        days_count += days;
    }
    if (days_count) {
        date += days_count + ' day(s) ';
    }
    date += hours + ':' + minutes + ':' + seconds
    return date
}


function formatDateToYYYYMMDDHHMM(date) {
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
  
    return `${month}.${day} ${hours}:${minutes}`;
}


function fillTotals(totals) {
    $('#top_active').text(totals.active);
    $('#top_done').text(totals.done);
    $('#top_dead').text(totals.dead);
    $('#top_total').text(formatToK(totals.total));
    $('#top_processed').text(formatToK(totals.processed));
    $('#top_remainig').text(formatToK(totals.queued));
}


function fillGraphTasksData(offset_name, graph_data) {
    let chartData = {
        labels: graph_data.labels,
        datasets: [{
            label: 'Processed',
            data: graph_data.lines.processed,
            fill: false,
            borderColor: 'rgb(75, 192, 192)',
            tension: 0.1
        },
        {
            label: 'Queued',
            data: graph_data.lines.queued,
            fill: false,
            borderColor: 'rgb(255, 99, 132)',
            tension: 0.1,
        },
        {
            label: 'Total',
            data: graph_data.lines.total,
            fill: false,
            borderColor: 'rgb(255, 170, 132)',
            tension: 0.1,
        }]
    }

    let ctx = document.getElementById(`tasksChart-${offset_name}`);

    tasksLineCharts[offset_name] = new Chart(ctx, {
        type: 'line',
        data: chartData
    });
}


function fillGraphSpeedsData(offset_name, graph_data) {
    let chartData = {
        labels: graph_data.labels,
        datasets: [{
            label: 'Load speed',
            data: graph_data.lines.load_speed,
            fill: false,
            borderColor: 'rgb(255, 99, 132)',
            tension: 0.1
        },
        {
            label: 'Processing speed',
            data: graph_data.lines.processing_speed,
            fill: false,
            borderColor: 'rgb(75, 192, 192)',
            tension: 0.1,
        }]
    }

    let ctx = document.getElementById(`speedsChart-${offset_name}`);

    speedsLineCharts[offset_name] = new Chart(ctx, {
        type: 'line',
        data: chartData
    });
}


function fillGraphProgressData(offset_name, progress) {
    let percent = progress || 0;
    let chartData = {
        labels: ['Processed', 'Queued'],
        datasets: [{
            label: 'Progress',
            data: [percent, 100 - percent],
            backgroundColor: [
            'rgb(54, 162, 235)',
            'rgb(255, 99, 132)',
            ],
            hoverOffset: 4
        }]
        };

    let ctx = document.getElementById(`progressPieChart-${offset_name}`);

    progressPieCharts[offset_name] = new Chart(ctx, {
        type: 'pie',
        data: chartData
    })
}


function refreshGraphTasksData(offset_name, graph_data) {
    chart = tasksLineCharts[offset_name];
    chart.data.labels = graph_data.labels;
    chart.data.datasets[0].data = graph_data.lines.processed;
    chart.data.datasets[1].data = graph_data.lines.queued;
    chart.data.datasets[2].data = graph_data.lines.total;
    chart.update();
}


function refreshGraphSpeedsData(offset_name, graph_data) {
    chart = speedsLineCharts[offset_name];
    chart.data.labels = graph_data.labels;
    chart.data.datasets[0].data = graph_data.lines.load_speed;
    chart.data.datasets[1].data = graph_data.lines.processing_speed;
    chart.update();
}


function refreshGraphProgressData(offset_name, progress) {
    let percent = progress || 0;
    chart = progressPieCharts[offset_name];
    chart.data.datasets[0].data = [percent, 100 - percent];
    chart.update();
}


function createTopicsAccordion(offsets) {
    const accordion = $('#topics_accordion');

    for (const [offset_name, values] of Object.entries(offsets)) {
        let label = LABELS[values.name] || values.name;
        if (label != values.name) {
            label += ` (${values.name})`;
        }
        let progress = values.processed_precent.toFixed(2);
        let total = getNumberWithCommas(values.total);
        let remaining = getNumberWithCommas(values.queued);
        let processed = getNumberWithCommas(values.processed);
        let load_speed = values.current_load_speed.toFixed(2);
        let processing_speed = values.current_processing_speed.toFixed(2);
        let status = values.status;
        let started = formatDateToYYYYMMDDHHMM(new Date(values.started));

        let finishes;
        if (values.finishes == "inf") {
            finishes = '\u221E';
        } else {
            finishes = formatDateToYYYYMMDDHHMM(new Date(values.finishes));
        }

        let time_left = values.time_left;
        if (typeof time_left == 'string') {
            time_left = '\u221E';
        } else {
            time_left = formatSecondsToTimeLeft(values.time_left.toFixed(0));
        }

        let status_icon;
        switch (status) {
            case 'active':
                status_icon = '<i class="bi bi-caret-right-square pe-2" style="font-size: 1rem; color:#407eff;"></i>';
                break;
            case 'done':
                status_icon = '<i class="bi bi-check-square pe-2" style="font-size: 1rem; color:lightgreen;"></i>';
                break;
            case 'dead':    
                status_icon = '<i class="bi bi-dash-square pe-2" style="font-size: 1rem; color:tomato;"></i>';
        }  

        let topicAccordionItem = `
            <div class="accordion-item ${offset_name}">
            <h2 class="accordion-header" id="panelsStayOpen-heading${offset_name}">
            <button class="accordion-button ${status} collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#panelsStayOpen-collapse${offset_name}" aria-expanded="false" aria-controls="panelsStayOpen-collapse${offset_name}">
                ${status_icon} ${label} | ${progress}%
            </button>
            </h2>
            <div id="panelsStayOpen-collapse${offset_name}" class="accordion-collapse collapse" aria-labelledby="panelsStayOpen-heading${offset_name}">
            <div class="accordion-body">
                <div class="row">
                    <div class="col-12 col-md-4 col-xl-3 topic-top-card">
                        <div class="py-3">
                        <div class="row m-0 px-2">
                            <div class="col-9 fs-2 topic-tasks-number topic-tasks-total">${total}</div>
                            <div class="col-3 mt-2"><i class="bi bi-list-nested" style="font-size: 1rem; color:#407eff;"></i></div>
                        </div>
                        <div class="row m-0 fs-6 text-secondary ps-3">Total</div>
                        </div>
                    </div>
                    <div class="col-12 col-md-4 col-xl-3 topic-top-card">
                        <div class="py-3">
                        <div class="row m-0 px-2">
                            <div class="col-9 fs-2 topic-tasks-number  topic-tasks-processed">${processed}</div>
                            <div class="col-3 mt-2"><i class="bi bi-list-check" style="font-size: 1rem; color:lightgreen;"></i></div>
                        </div>
                        <div class="row m-0 fs-6 text-secondary ps-3">Processed</div>
                        </div>
                    </div>
                    <div class="col-12 col-md-4 col-xl-3 topic-top-card">
                        <div class="py-3">
                        <div class="row m-0 px-2">
                            <div class="col-9 fs-2 topic-tasks-number topic-tasks-queued">${remaining}</div>
                            <div class="col-3 mt-2"><i class="bi bi-list-ul" style="font-size: 1rem; color: gold;"></i></div>
                        </div>
                        <div class="row m-0 fs-6 text-secondary ps-3">Queued</div>
                        </div>
                    </div>
    
                    <div class="col-12 col-xl-3 mt-4 mt-xl-0 topic-top-card">
                        <dev class="row">
                        <div class="col-4 col-lg-6 topic-top-card">
                            <div class="py-3">
                            <div class="row m-0 px-2">
                                <div class="col-9 fs-4 fw-bold"><span class="topic-speed-load">${load_speed}</span><span class="fs-5 text-secondary fw-normal">/s</span></div>
                            </div>
                            <div class="row m-0 fs-6 text-secondary ps-3">Load speed</div>
                            </div>
                        </div>
                        <div class="col-4 col-lg-6 topic-top-card">
                            <div class="py-3">
                            <div class="row m-0 px-2">
                                <div class="col-9 fs-4 fw-bold"><span class="topic-speed-processing">${processing_speed}</span><span class="fs-5 text-secondary fw-normal">/s</span></div>
                            </div>
                            <div class="row m-0 fs-6 text-secondary ps-3">Proc. speed</div>
                            </div>
                        </div>
    
                        <div class="col-4 d-block d-lg-none topic-top-card">
                            <div class="py-3">
                            <div class="row m-0 px-2">
                                <div class="col-9 fs-4 fw-bold"><span class="topic-progress">${progress}</span>%</div>
                            </div>
                            <div class="row m-0 fs-6 text-secondary ps-3"><span>Left <span class="topic-lime-left">${time_left}</span></span></div>
                            </div>
                        </div>
                        </dev>
                    </div>
                </div>
    
                <div class="row mt-4">
                    <div class="col-3 d-none d-lg-block">
                    <div class="row">
                        <span class="fs-4 fw-500 text-center">Progress</span>
                    </div>
                    <div class="row px-4">
                        <div><canvas class="chart-container" id="progressPieChart-${offset_name}"></canvas></div>
                    </div>
                    <div class="row mt-2 text-center">
                        <span class="fs-6 fw-500">Time left</span>
                    </div>
                    <div class="row text-center">
                        <span class="fs-5 topic-lime-left">${time_left}</span>
                    </div>
                    <hr>
                    <div class="row text-center">
                        <div class="col-6"><span class="fw-500">Started</span><br><span class="topic-time-started">${started}</span></div>
                        <div class="col-6"><span class="fw-500">Finishes</span><br><span class="topic-time-finishes">${finishes}</span></div>
                    </div>
                    </div>
                    <div class="col-12 col-lg-9">
                        <div><canvas class="chart-container" id="tasksChart-${offset_name}"></canvas></div>
                    </div>
                </div>

                <div class="row mt-4">
                    <div class="col-12">
                        <div><canvas class="chart-container speeds" id="speedsChart-${offset_name}"></canvas></div>
                    </div>
                </div>
                </div>
            </div>
            </div>
        </div>`

        accordion.append(topicAccordionItem);
        fillGraphTasksData(offset_name, values.full_tasks_graphs);
        fillGraphSpeedsData(offset_name, values.full_speeds_graphs);
        fillGraphProgressData(offset_name, progress);
    }
}


function fillTopicsAccordion(metrics) {
    const accordion = $('#topics_accordion');

    for (const [offset_name, values] of Object.entries(metrics)) {
        let label = LABELS[values.name] || values.name;
        if (label != values.name) {
            label += ` (${values.name})`;
        }
        let progress = values.processed_precent.toFixed(2);
        let total = getNumberWithCommas(values.total);
        let remaining = getNumberWithCommas(values.queued);
        let processed = getNumberWithCommas(values.processed);
        let load_speed = values.current_load_speed.toFixed(2);
        let processing_speed = values.current_processing_speed.toFixed(2);
        let status = values.status;
        let started = formatDateToYYYYMMDDHHMM(new Date(values.started));

        let finishes;
        if (values.finishes == "inf") {
            finishes = '\u221E';
        } else {
            finishes = formatDateToYYYYMMDDHHMM(new Date(values.finishes));
        }

        let time_left = values.time_left;
        if (typeof time_left == 'string') {
            time_left = '\u221E';
        } else {
            time_left = formatSecondsToTimeLeft(values.time_left.toFixed(0));
        }

        let status_icon;
        switch (status) {
            case 'active':
                status_icon = '<i class="bi bi-caret-right-square pe-2" style="font-size: 1rem; color:#407eff;"></i>';
                break;
            case 'done':
                status_icon = '<i class="bi bi-check-square pe-2" style="font-size: 1rem; color:lightgreen;"></i>';
                break;
            case 'dead':    
                status_icon = '<i class="bi bi-dash-square pe-2" style="font-size: 1rem; color:tomato;"></i>';
        }

        $(`.accordion-item.${offset_name} .accordion-button`).removeClass('active done dead');
        $(`.accordion-item.${offset_name} .accordion-button`).addClass(status);
        $(`.accordion-item.${offset_name} .accordion-button`).html(`${status_icon} ${label} | ${progress}%`);
        $(`.accordion-item.${offset_name} .topic-tasks-total`).text(total);
        $(`.accordion-item.${offset_name} .topic-tasks-processed`).text(processed);
        $(`.accordion-item.${offset_name} .topic-tasks-queued`).text(remaining);
        $(`.accordion-item.${offset_name} .topic-speed-load`).text(load_speed);
        $(`.accordion-item.${offset_name} .topic-speed-processing`).text(processing_speed);
        $(`.accordion-item.${offset_name} .topic-progress`).text(progress);
        $(`.accordion-item.${offset_name} .topic-lime-left`).text(time_left);
        $(`.accordion-item.${offset_name} .topic-time-started`).text(started);
        $(`.accordion-item.${offset_name} .topic-time-finishes`).text(finishes);

        refreshGraphTasksData(offset_name, values.full_tasks_graphs);
        refreshGraphSpeedsData(offset_name, values.full_speeds_graphs);
        refreshGraphProgressData(offset_name, progress);
    }
        
}


function loadData() {
    $.ajax({
        type: 'GET',
        url: `${API_URL}/metrics/dashboard`,
        success: (dashboard) => {
            fillTotals(dashboard.totals);
            createTopicsAccordion(dashboard.metrics);
        },
        error: (res) => {
            //
        },
        timeout: 3000
    });
}


function refreshData() {
    $.ajax({
        type: 'GET',
        url: `${API_URL}/metrics/dashboard`,
        success: (dashboard) => {
            fillTotals(dashboard.totals);
            fillTopicsAccordion(dashboard.metrics);
        },
        error: (res) => {
            //
        },
        timeout: 3000
    });
}


window.onload = () => {
    loadData();
    setInterval(refreshData, 15000);
};
