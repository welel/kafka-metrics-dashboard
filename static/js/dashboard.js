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
    return number.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
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
    let active = 0;
    let done = 0;
    let dead = 0;
    let total = 0;
    let processed = 0;
    let remainig = 0;

    for (const [offset_name, values] of Object.entries(offsets)) {
        total += values.total;
        processed += values.processed;
        remainig += values.remaining;

        if (values.status === 'active') {
            active += 1;
        } else if (values.status === 'done') {
            done += 1;
        } else if (values.status === 'dead') {
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
    var accordion = $('#topics_accordion');
    for (const [offset_name, values] of Object.entries(offsets)) {
        let label = LABELS[values.label] || values.label;
        let progress = values.processed_precent.toFixed(2);
        let total = getNumberWithCommas(values.total);
        let remaining = getNumberWithCommas(values.remaining);
        let processed = getNumberWithCommas(values.processed);
        let load_speed = values.load_speed.toFixed(2);
        let processing_speed = values.processing_speed.toFixed(2);
        let time_left = values.time_left;
        if (typeof time_left == 'string') {
            time_left = '\u221E';
        } else {
            time_left = formatSecondsToTimeLeft(values.time_left.toFixed(0));
        }

        var topicAccordionItem = `<div class="accordion-item">
        <h2 class="accordion-header" id="panelsStayOpen-heading${offset_name}">
          <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#panelsStayOpen-collapse${offset_name}" aria-expanded="false" aria-controls="panelsStayOpen-collapse${offset_name}">
            ${label} | ${progress}%
          </button>
        </h2>
        <div id="panelsStayOpen-collapse${offset_name}" class="accordion-collapse collapse" aria-labelledby="panelsStayOpen-heading${offset_name}">
          <div class="accordion-body">
              <div class="row row row-cols-1 row-cols-sm-3 row-cols-lg-6 text-white text-center">
                  <div class="col-2 py-3" style="background-color: #407eff; border-top: 1px solid black; border-left: 1px solid black; border-bottom: 1px solid black;"><b>${total}</b><br>total</div>
                  <div class="col-2 py-3" style="background-color: #407eff; border-top: 1px solid black; border-left: 1px solid black; border-bottom: 1px solid black;"><b>${processed}</b><br>processed</div>
                  <div class="col-2 py-3" style="background-color: #407eff; border-top: 1px solid black; border-left: 1px solid black; border-bottom: 1px solid black;"><b>${remaining}</b><br>queued</div>
                  <div class="col-3 py-3" style="background-color: limegreen; border-top: 1px solid black; border-left: 1px solid black; border-bottom: 1px solid black;"><b>${load_speed}/s</b><br>load speed</div>
                  <div class="col-3 py-3" style="background-color: limegreen; border: 1px solid black;"><b>${processing_speed}/s</b><br>processing speed</div>
              </div>
              <div class="row text-center">
                  <div class="col-6">
                      <div class="row">
                          <div class="col-6 py-3 fs-2"><p style="border: 1px solid blue;">${progress}%<br><span class="fs-6">Processed</span></p></div>
                          <div class="col-6 py-3 fs-2"><p style="border: 1px solid blue;">${time_left}<br><span class="fs-6">Left</span></p></div>
                      </div>
                  </div>
                  <div class="col-6">
                      <div class="row">
                          <div class="col-6 py-3 fs-2"><p style="border: 1px solid blue;">23.09 23:00<br><span class="fs-6">Started</span></p></div>
                          <div class="col-6 py-3 fs-2"><p style="border: 1px solid blue;">24.05 11:00<br><span class="fs-6">Should end</span></p></div>
                      </div>
                  </div>
                  <div class="row">
                    <div>
                        <canvas class="chart-container" id="chart-${offset_name}"></canvas>
                    </div>
                  </div>
              </div>
          </div>
        </div>
        </div>`;

        accordion.append(topicAccordionItem);
    }
}

// var chartData = {
//     labels: ['January', 'February', 'March', 'April', 'May', 'June', 'July'],
//     datasets: [{
//         label: 'My First Dataset',
//         data: [0, 200, 1000, 25000, 15000, 5000, 40],
//         fill: false,
//         borderColor: 'rgb(75, 192, 192)',
//         tension: 0.1
//     },
//     {
//         label: 'My Second Dataset', // Label for the second line
//         data: [30, 1000, 6000, 70000, 50000, 400, 30], // Data for the second line
//         fill: false,
//         borderColor: 'rgb(255, 99, 132)', // Color for the second line
//         tension: 0.1,
//     }]
// }

function fillGraphsData(offsets) {
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

        let ctx = document.getElementById(`chart-${offset_name}`);

        new Chart(ctx, {
            type: 'line',
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
        timeout: 3000
    });
}


function loadData() {
    $.ajax({
        type: 'GET',
        url: 'http://localhost:8000/metrics/offsets?sec=60000',
        success: (offsets) => {
            fillTotals(offsets);
            // fillTopicsAccordion(offsets);
            // requestGraphsData();

            $.when(fillTopicsAccordion(offsets)).then(function(){
                requestGraphsData();
            })
        },
        error: (res) => {
            //
        },
        timeout: 3000
    });
}

window.onload = () => {
    loadData();
};
