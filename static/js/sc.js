document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('register-link').addEventListener('click', function() {
        document.getElementById('login-form').style.display = 'none';
        document.getElementById('register-form').style.display = 'block';
    });

    document.getElementById('login-link').addEventListener('click', function() {
        document.getElementById('register-form').style.display = 'none';
        document.getElementById('login-form').style.display = 'block';
    });
});

function togglePassword(fieldId) {
    var field = document.getElementById(fieldId);
    if (field.type === 'password') {
        field.type = 'text';
    } else {
        field.type = 'password';
    }
}
