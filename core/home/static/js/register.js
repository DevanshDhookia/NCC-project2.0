$(document).ready(() => {
    $("#senior").hide();
})

function otpchange() {
    otpl = $("#otp-field")
    valu = $("#otp_field").val();
    if(otpl && valu.length === 0) {
        $("#password1").prop("readonly", true)
        $("#password2").prop("readonly", true)
        $("#generate-otp-btn").attr("disabled", false)
    } else {
        $("#password1").prop("readonly", false)
        $("#password2").prop("readonly", false)
        $("#generate-otp-btn").attr("disabled", true)
    }
    
}

function onUserTypeChange() {
    val = $("#user_type").val();
    options = "<option selected disabled>Select senior</option>"
    if(val === 'clerk') {
        $("#senior").show();
        $.ajax({
            type: "GET",
            url: "/get-seniors/"+val+"/",
            complete: function(data) {
                if(data.responseJSON.status === 200 && data.responseJSON.data) {
                    data.responseJSON.data.forEach((item) => {
                        options += `<option value=${item.id}>${item.username}</option>`
                    })
                    $("#senior").html(options)
                }
            }
        });
    } else {
        $("#senior").hide();
    }
}