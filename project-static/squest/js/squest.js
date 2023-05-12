$(document).ready(function () {
    $('[data-toggle="popover"]').popover({
        placement: 'top',
        trigger: 'hover'
    });
    // adapt side bar height to the current page
    $('.main-sidebar').height($(document).outerHeight());

    $('.ajax_sync_all_job_template').click(sync_all_job_template);
    $('.ajax_sync_job_template').click(sync_job_template);

    // pool table
    var disabled_column_list = ["p-factor", "c-factor"];
    var poolTable = $('#pool_table').DataTable( {
        dom: 'Bfrtip',
        buttons: [
            'csv', 'colvis', 'pageLength'
        ],
        lengthMenu: [
            [50, 100, 200, -1],
            [50, 100, 200, 'All'],
        ],
        fixedColumns:   {
            left: 1,
        }
    });


    // Apply the filter to remove refactors by default
    // depreacted resource tracker v1
    // var titles = $('#pool_table thead th');
    // poolTable.columns().eq(0).each(function (colIdx) {
    //     var column = poolTable.columns(colIdx);
    //     var title = titles.eq(colIdx).text();
    //     if (containsAny(title, disabled_column_list)){
    //         // console.log("disable colum id:" + colIdx)
    //         column.visible(false, false);
    //     }
    // });
    // poolTable.reload();
});

function containsAny(str, substrings) {
    for (var i = 0; i !== substrings.length; i++) {
       var substring = substrings[i];
       if (str.indexOf(substring) !== - 1) {
            // console.log("found:" + str );
            return true;
       }
    }
    return false;
}

function add_tab_management() {
    var hash = window.location.hash;
    hash && $('ul.nav.nav-pills a[href="' + hash + '"]').tab('show');
    $('ul.nav.nav-pills a').click(function (e) {
        $(this).tab('show');
        var scrollmem = $('body').scrollTop();
        window.location.hash = this.hash;
    });
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrf_token = getCookie('csrftoken');

function sync_all_job_template() {
    const tower_id = $(this).data('tower-id');
    const url_sync = $(this).data('url-sync');
    const url_job_template = $(this).data('url-job-template');
    const sync_button_id = "tower_" + tower_id;
    $.ajax({
        url: url_sync,
        method: 'POST',
        data: {
            csrfmiddlewaretoken: csrf_token
        },
    }).done((res) => {
        $(document).Toasts('create', {
            title: 'Tower sync',
            body: 'Started',
            autohide: true,
            delay: 3000,
            class: 'bg-info mr-3 my-3'
        });
        // disable sync button
        document.getElementById(sync_button_id).classList.add('disabled');
        var interval_id = setInterval(function () {
            getTowerUpdateStatus(res.task_id, tower_id, url_job_template, interval_id);
        }, 2000);

    }).fail((err) => {
        alert_error("Error during API call");
        $(document).Toasts('create', {
            title: 'Tower sync',
            body: 'Error',
            autohide: true,
            delay: 3000,
            class: 'bg-danger mr-3 my-3'
        });
        console.log(err);
    });
}

function getTowerUpdateStatus(taskID, tower_id, url_job_template, interval_id) {
    const sync_button_id = "tower_" + tower_id;
    const job_template_count = "job_template_count_" + tower_id;
    $.ajax({
        url: `/api/tasks/${taskID}/`,
        method: 'GET',
        data: {
            csrfmiddlewaretoken: csrf_token
        },
    }).done((res) => {
        const taskStatus = res.status;
        if (taskStatus === 'SUCCESS') {
            $(document).Toasts('create', {
                title: 'Tower sync',
                body: 'Complete',
                autohide: true,
                delay: 3000,
                class: 'bg-success mr-3 my-3'
            });
            // enable back sync button
            document.getElementById(sync_button_id).classList.remove('disabled');
            $.ajax({
                url: url_job_template,
                method: 'GET',
                data: {
                    csrfmiddlewaretoken: csrf_token
                },
            }).done((res) => {
                document.getElementById(job_template_count).innerText = res.count;
            }).fail((err) => {
                document.getElementById(sync_button_id).classList.remove('disabled');
            });
            clearInterval(interval_id);
            return true;

        }
        if (taskStatus === 'FAILURE') {
            $(document).Toasts('create', {
                title: 'Tower sync',
                body: 'Failed',
                autohide: true,
                delay: 3000,
                class: 'bg-danger mr-3 my-3'
            });
            // enable back sync button
            document.getElementById(sync_button_id).classList.remove('disabled');
            clearInterval(interval_id);
            return false;
        }
    }).fail((err) => {
        $(document).Toasts('create', {
            title: 'Tower sync',
            body: 'Failed',
            autohide: true,
            delay: 3000,
            class: 'bg-danger mr-3 my-3',
        });
        // enable back sync button
        document.getElementById(sync_button_id).classList.remove('disabled');
        clearInterval(interval_id);
        return false;
    });
}

function sync_job_template() {
    const job_template_id = $(this).data('job-template-id');
    const url_sync = $(this).data('url-sync');
    const url_job_template_detail = $(this).data('url-job-template-detail');

    const sync_button_id = "job_template_" + job_template_id;
    $.ajax({
        url: url_sync,
        method: 'POST',
        data: {
            csrfmiddlewaretoken: csrf_token
        },
    }).done((res) => {
        $(document).Toasts('create', {
            title: 'Job template sync from Tower/AWX',
            body: 'Started',
            autohide: true,
            delay: 3000,
            class: 'bg-info mr-3 my-3'
        });
        // disable sync button
        document.getElementById(sync_button_id).classList.add('disabled');
        var interval_id = setInterval(function () {
            getJobTemplateUpdateStatus(res.task_id, job_template_id, url_job_template_detail, interval_id);
        }, 2000);

    }).fail((err) => {
        alert_error("Error during API call");
        $(document).Toasts('create', {
            title: 'Job template sync from Tower/AWX',
            body: 'Error',
            autohide: true,
            delay: 3000,
            class: 'bg-danger mr-3 my-3'
        });
        console.log(err);
    });
}

function getJobTemplateUpdateStatus(taskID, job_template_id, url_job_template_detail, interval_id) {
    const sync_button_id = "job_template_" + job_template_id;
    const icon_id = "icon_" + job_template_id;
    const html_name = $("#job_template_"+job_template_id+" td.job_template_name");
    $.ajax({
        url: `/api/tasks/${taskID}/`,
        method: 'GET',
        data: {
            csrfmiddlewaretoken: csrf_token
        },
    }).done((res) => {
        const taskStatus = res.status;
        if (taskStatus === 'SUCCESS') {
            $(document).Toasts('create', {
                title: 'Tower sync',
                body: 'Complete',
                autohide: true,
                delay: 3000,
                class: 'bg-success mr-3 my-3'
            });
            // enable back sync button
            document.getElementById(sync_button_id).classList.remove('disabled');
            $.ajax({
                url: url_job_template_detail,
                method: 'GET',
                data: {
                    csrfmiddlewaretoken: csrf_token
                },
            }).done((res) => {
                document.getElementById(icon_id).classList.remove('fa-check');
                document.getElementById(icon_id).classList.remove('text-success');
                document.getElementById(icon_id).classList.remove('fa-times');
                document.getElementById(icon_id).classList.remove('text-danger');
                if (res.is_compliant) {
                    document.getElementById(icon_id).classList.add('fa-check');
                    document.getElementById(icon_id).classList.add('text-success');
                } else {
                    document.getElementById(icon_id).classList.add('fa-times');
                    document.getElementById(icon_id).classList.add('text-danger');
                }
                html_name.html(res.name);

            });
            clearInterval(interval_id);
            return true;
        }
        if (taskStatus === 'FAILURE') {
            $(document).Toasts('create', {
                title: 'Tower sync',
                body: 'Failed',
                autohide: true,
                delay: 3000,
                class: 'bg-danger mr-3 my-3'
            });
            // enable back sync button
            document.getElementById(sync_button_id).classList.remove('disabled');
            clearInterval(interval_id);
            return false;
        }

    }).fail((err) => {
        console.log(err);
        $(document).Toasts('create', {
            title: 'Tower sync',
            body: 'Failed',
            autohide: true,
            delay: 3000,
            class: 'bg-danger mr-3 my-3',
        });
        // enable back sync button
        document.getElementById(sync_button_id).classList.remove('disabled');
        clearInterval(interval_id);
        return false;
    });
}

function showLoaderOnClick() {
    $(document).Toasts('create', {
        icon: 'fas fa-chess-rook',
        title: 'Tower',
        body: 'Starting job template. Please wait...',
        autohide: true,
        delay: 5000,
        class: 'bg-info mr-3 my-3'
    });
}
