$(document).ready(function () {
    var params = {"order": [], "columnDefs": [{"targets": 'no-sort', "orderable": false,}]};
    $('#tower_list').DataTable(params);
    $('#job_template_list').DataTable(params);
    $('#service_list').DataTable(params);
    $('#request_list').DataTable(params);
    $('#customer_request_operation_list').DataTable(params);
    $('#announcement_list').DataTable(params);

    $('[data-toggle="popover"]').popover({
        placement: 'top',
        trigger: 'hover'
    });
    // adapt side bar height to the current page
    $('.main-sidebar').height($(document).outerHeight());
});

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

function sync_all_job_template(tower_id) {
    const sync_button_id = "tower_" + tower_id;
    $.ajax({
        url: '/settings/tower/' + tower_id + '/sync/',
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
        setTimeout(function () {
            getTowerUpdateStatus(res.task_id, tower_id);
        }, 1000);

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

function getTowerUpdateStatus(taskID, tower_id) {
    const sync_button_id = "tower_" + tower_id;
    const job_template_count = "job_template_count_" + tower_id;
    $.ajax({
        url: `/tasks/${taskID}/`,
        method: 'GET',
        data: {
            csrfmiddlewaretoken: csrf_token
        },
    }).done((res) => {
        // console.log(res);
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
                url: `/api/service_catalog/admin/job_template/`,
                method: 'GET',
                data: {
                    csrfmiddlewaretoken: csrf_token
                },
            }).done((res) => {
                document.getElementById(job_template_count).innerText = res.length;
            });
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
    });
}

function sync_job_template(tower_id, job_template_id) {
    const sync_button_id = "job_template_" + job_template_id;
    $.ajax({
        url: '/settings/tower/' + tower_id + '/sync/' + job_template_id,
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
        setTimeout(function () {
            getJobTemplateUpdateStatus(res.task_id, job_template_id);
        }, 1000);

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

function getJobTemplateUpdateStatus(taskID, job_template_id) {
    const sync_button_id = "job_template_" + job_template_id;
    const icon_id = "icon_" + job_template_id;
    const name_id = "name_" + job_template_id;
    $.ajax({
        url: `/tasks/${taskID}/`,
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
                url: '/api/service_catalog/admin/job_template/' + job_template_id,
                method: 'GET',
                data: {
                    csrfmiddlewaretoken: csrf_token
                },
            }).done((res) => {
                console.log(res);
                document.getElementById(icon_id).classList.remove('fa-check');
                document.getElementById(icon_id).classList.remove('text-success');
                document.getElementById(icon_id).classList.remove('fa-times');
                document.getElementById(icon_id).classList.remove('text-danger');
                if (res.compliant) {
                    document.getElementById(icon_id).classList.add('fa-check');
                    document.getElementById(icon_id).classList.add('text-success');
                } else
                {
                    document.getElementById(icon_id).classList.add('fa-times');
                    document.getElementById(icon_id).classList.add('text-danger');
                }
                document.getElementById(name_id).innerText=res.name;

            });
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
