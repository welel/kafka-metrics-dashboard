LABELS = {
    'db_service': 'DB Service',
    'tokopedia_1': 'Tokopedia Category Pages (tokopedia_1)',
    'tokopedia_2': 'Tokopedia Products (tokopedia_2)',
    'tokopedia_3': 'Tokopedia Sellers (tokopedia_3)',
}


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


function fillTotals(offsets) {
    let active = 0,
        done = 0,
        dead = 0,
        total = 0,
        processed = 0,
        remainig = 0;

    for (const [offset_name, values] of Object.entries(offsets)) {
        total += values.total;
        processed += values.processed;
        remainig += values.remaining;

        switch (values.status) {
            case 'active':
                active += 1;
                break;
            case 'done':
                done += 1;
                break;
            case 'dead':
                dead += 1;
        }  
    }

    $('#top_active').text(active);
    $('#top_done').text(done);
    $('#top_dead').text(dead);
    $('#top_total').text(formatToK(total));
    $('#top_processed').text(formatToK(processed));
    $('#top_remainig').text(formatToK(remainig));
}

function fillTopicsAccordion(offsets) {
    const accordion = $('#topics_accordion');

    for (const [offset_name, values] of Object.entries(offsets)) {
        let label = LABELS[values.name] || values.name;
        let progress = values.processed_precent.toFixed(2);
        let total = getNumberWithCommas(values.total);
        let remaining = getNumberWithCommas(values.remaining);
        let processed = getNumberWithCommas(values.processed);
        let load_speed = values.load_speed.toFixed(2);
        let processing_speed = values.processing_speed.toFixed(2);
        let status = values.status;

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
            <div class="accordion-item">
            <h2 class="accordion-header" id="panelsStayOpen-heading${offset_name}">
            <button class="accordion-button accordion-${status}-btn collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#panelsStayOpen-collapse${offset_name}" aria-expanded="false" aria-controls="panelsStayOpen-collapse${offset_name}">
                ${status_icon} ${label} | ${progress}%
            </button>
            </h2>
            <div id="panelsStayOpen-collapse${offset_name}" class="accordion-collapse collapse" aria-labelledby="panelsStayOpen-heading${offset_name}">
            <div class="accordion-body">
                <div class="row">
                    <div class="col-12 col-md-4 col-xl-3 topic-top-card">
                        <div class="py-3">
                        <div class="row m-0 px-2">
                            <div class="col-9 fs-2 topic-tasks-number">${total}</div>
                            <div class="col-3 mt-2"><i class="bi bi-list-nested" style="font-size: 1rem; color:#407eff;"></i></div>
                        </div>
                        <div class="row m-0 fs-6 text-secondary ps-3">Total</div>
                        </div>
                    </div>
                    <div class="col-12 col-md-4 col-xl-3 topic-top-card">
                        <div class="py-3">
                        <div class="row m-0 px-2">
                            <div class="col-9 fs-2 topic-tasks-number">${processed}</div>
                            <div class="col-3 mt-2"><i class="bi bi-list-check" style="font-size: 1rem; color:lightgreen;"></i></div>
                        </div>
                        <div class="row m-0 fs-6 text-secondary ps-3">Processed</div>
                        </div>
                    </div>
                    <div class="col-12 col-md-4 col-xl-3 topic-top-card">
                        <div class="py-3">
                        <div class="row m-0 px-2">
                            <div class="col-9 fs-2 topic-tasks-number">${remaining}</div>
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
                                <div class="col-9 fs-4 fw-bold">${load_speed}<span class="fs-5 text-secondary fw-normal">/s</span></div>
                            </div>
                            <div class="row m-0 fs-6 text-secondary ps-3">Load speed</div>
                            </div>
                        </div>
                        <div class="col-4 col-lg-6 topic-top-card">
                            <div class="py-3">
                            <div class="row m-0 px-2">
                                <div class="col-9 fs-4 fw-bold">${processing_speed}<span class="fs-5 text-secondary fw-normal">/s</span></div>
                            </div>
                            <div class="row m-0 fs-6 text-secondary ps-3">Proc. speed</div>
                            </div>
                        </div>
    
                        <div class="col-4 d-block d-lg-none topic-top-card">
                            <div class="py-3">
                            <div class="row m-0 px-2">
                                <div class="col-9 fs-4 fw-bold">${progress}%</div>
                            </div>
                            <div class="row m-0 fs-6 text-secondary ps-3">Left ${time_left}</div>
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
                        <span class="fs-5">${time_left}</span>
                    </div>
                    <hr>
                    <div class="row text-center">
                        <div class="col-6"><span class="fw-500">Started</span><br>dd.mm HH:MM</div>
                        <div class="col-6"><span class="fw-500">Finishes</span><br>dd.mm HH:MM</div>
                    </div>
                    </div>
                    <div class="col-12 col-lg-9">
                        <style>
                            /* Set the maximum height for the container */
                            .chart-container {
                                max-height: 400px; /* Adjust this value as needed */
                                overflow-y: auto; /* Enable vertical scrolling if needed */
                            }
                        </style>
                        <div><canvas class="chart-container" id="tasksChart-${offset_name}"></canvas></div>
                    </div>
                </div>
                </div>
            </div>
            </div>
        </div>`

        accordion.append(topicAccordionItem);
    }
}

function fillGraphsData(offsets) {
    // Tasks Chart
    for (const [offset_name, values] of Object.entries(offsets)) {
        let chartData = {
            labels: values.requested,
            datasets: [{
                label: 'Processed',
                data: values.processed,
                fill: false,
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1
            },
            {
                label: 'Queued',
                data: values.queued,
                fill: false,
                borderColor: 'rgb(255, 99, 132)',
                tension: 0.1,
            },
            {
                label: 'Total',
                data: values.total,
                fill: false,
                borderColor: 'rgb(255, 170, 132)',
                tension: 0.1,
            }]
        }

        let ctx = document.getElementById(`tasksChart-${offset_name}`);

        new Chart(ctx, {
            type: 'line',
            data: chartData
        })
    }

    // Progress Pie Chart
    for (const [offset_name, values] of Object.entries(offsets)) {
        let percent = values.processed_precent.slice(-1)[0] || 0;
        let chartData = {
            labels: ['Processed', 'Queued'],
            datasets: [{
              label: 'Progress',
              data: [percent, 100 - percent],
              backgroundColor: [
                'rgb(255, 99, 132)',
                'rgb(54, 162, 235)',
              ],
              hoverOffset: 4
            }]
          };

        let ctx = document.getElementById(`progressPieChart-${offset_name}`);

        new Chart(ctx, {
            type: 'pie',
            data: chartData
        })
    }
}


function requestGraphsData() {
    $.ajax({
        type: 'GET',
        url: 'http://localhost:8000/metrics/graph',
        success: (offsets) => {
            fillGraphsData(offsets);
        },
        error: (res) => {
            //
        },
        timeout: 60000
    });
}


function loadData() {
    $.ajax({
        type: 'GET',
        url: 'http://localhost:8000/metrics/offsets?sec=600',
        success: (offsets) => {
            fillTotals(offsets);

            $.when(fillTopicsAccordion(offsets)).then(function(){
                requestGraphsData();
            })
        },
        error: (res) => {
            //
        },
        timeout: 60000
    });
}

window.onload = () => {
    loadData();
};
