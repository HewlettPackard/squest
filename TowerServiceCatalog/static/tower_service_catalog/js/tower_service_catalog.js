$(document).ready( function () {
    $('#tower_list').DataTable();
} );

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

function sync_tower(id){
    $.ajax({
        url: '/tower/' + id + '/sync_tower/',
        method: 'POST',
        data: {
            csrfmiddlewaretoken: csrf_token
        },
    }).done((res) => {
        // getStatus(res.task_id);
        $(document).Toasts('create', {
            title: 'Tower sync',
            body: 'Started',
            autohide: true,
            delay: 3000,
            class: 'bg-info'
        })
        console.log(res.task_id);
        getStatus(res.task_id);

    }).fail((err) => {
        alert_error("Error during API call");
        $(document).Toasts('create', {
            title: 'Tower sync',
            body: 'Error',
            autohide: true,
            delay: 3000,
            class: 'bg-danger'
        })
        console.log(err);
    });
}

function getStatus(taskID) {
    $.ajax({
        url: `/tasks/${taskID}/`,
        method: 'GET',
        data: {
            csrfmiddlewaretoken: csrf_token
        },
    })
        .done((res) => {
            console.log(res);
            const taskStatus = res.status;

            if (taskStatus === 'SUCCESS'){
                $(document).Toasts('create', {
                    title: 'Tower sync',
                    body: 'Complete',
                    autohide: true,
                    delay: 3000,
                    class: 'bg-success'
                })
                return true;
            }
            if (taskStatus === 'FAILURE'){
                $(document).Toasts('create', {
                    title: 'Tower sync',
                    body: 'Failed',
                    autohide: true,
                    delay: 3000,
                    class: 'bg-danger'
                })
                return false;
            }
            setTimeout(function() {
                getStatus(taskID);
            }, 1000);
        })
        .fail((err) => {
            console.log(err);
            $(document).Toasts('create', {
                title: 'Tower sync',
                body: 'Failed',
                autohide: true,
                delay: 3000,
                class: 'bg-danger'
            })
        });
}
