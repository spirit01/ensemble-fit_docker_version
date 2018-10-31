$(function () {
    validation();
    setPlaceholders();
    setUsername();
});

function setUsername() {
    $('#username').val($('#username_hid_inp').val());
    $('#email').val($('#email_hid_inp').val());
}

//sets HTML placeholder attribute for specified textboxes
function setPlaceholders(){
    $('#user_email').prop('placeholder', "Email");
    $('#login_email').prop('placeholder', "Email");
    $('#login_password').prop('placeholder', "Password");

}

function validation() {
    $('#register_form').validate({
        rules: {
            username: {
                required: true
            }
        },
        messages: {
            password2: {
                equalTo: "Please enter the same password again."
            },
            register_email: {
                remote: "Email address is taken, please use a different one."
            },
            username: {
                remote: "Username is taken, please use a different one."
            }
        },
        errorElement: 'span'
    });
}