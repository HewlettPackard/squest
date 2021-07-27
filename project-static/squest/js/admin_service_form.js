$(function () {
    $('#id_billing_1 label').each(
        function () {
            $(this).on('click', function () {
                $("#id_billing_group_id").val("");
                $("#billing_group_id").hide();
                $("#id_billing_group_is_shown").prop('disabled', true);
                $("#id_billing_group_is_shown").prop('checked', true);
            })
        }
    )
    $("#id_billing_0").on('click', function () {
        $("#billing_group_id").show();
        $("#id_billing_group_is_shown").prop('disabled', false);


    })
});