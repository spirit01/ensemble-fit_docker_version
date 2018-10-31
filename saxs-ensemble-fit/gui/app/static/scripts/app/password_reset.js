$(function () {
    validation();
});

function validation() {
    $('#password_reset_form').validate({
        rules: {
            user_email: {
                required: true,
                email: true
            },
            new_password: {
                required: true,
                minlength: 8
            },
            new_password_confirm: {
                required: true,
                minlength: 8,
                equalTo: "#new_password"
            }
        },
        messages: {
            new_password_confirm: {
                equalTo: "Please enter the same password again."
            }
        },
        errorElement: 'span'
    });
}
