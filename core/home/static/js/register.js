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
