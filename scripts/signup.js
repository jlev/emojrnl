$(document).ready(function() {
    EMOJRNL_URL = 'http://my.emojr.nl/';
    EMOJRNL_URL = 'http://localhost:8000/'

    $('form#getstarted').submit(function(event) {
        event.preventDefault();

        var phone = $('input[type=tel]').val()
            .replace(/[\(\)\-\+]/,'');
        console.log('phone', phone);
        // TODO really validate e164

        $.post(EMOJRNL_URL+'sms/signup/1'+phone+'/')
         .done(function(data) {
            if (data.message === 'create') {
                alert('👍\n😅📓📲');
            } else if (data.message == 'exists') {
                // TODO for security, send user a verification text
                // temp, redirect to your page
                window.location.assign(EMOJRNL_URL+'#'+data.hashid);
            } else if (data.message == 'confirm') {
                window.location.assign(EMOJRNL_URL+'#'+data.hashid);
            }
         })
         .fail(function(data) {
            console.error(data);
            alert('😞');
         })
    });
});