
function calculateTotalMarks(){
    selected_val = Number($('#bonus_marks_cat').find(":selected").attr("percentage"));
    p1_total = Number($('#res_p1_w').val())+Number($('#res_p1_p').val());
    p2_total = Number($('#res_p2_w').val())+Number($('#res_p2_p').val());
    p3_total = Number($('#res_p3_w').val());
    p4_total = Number($('#res_p4_w').val())+Number($('#res_p4_p').val());
    $('#res_p1_t').val(Number(p1_total.toFixed(2))).prop("readonly", true);
    $('#res_p2_t').val(Number(p2_total.toFixed(2))).prop("readonly", true);
    $('#res_p4_t').val(Number(p4_total.toFixed(2))).prop("readonly", true);
    bef_amount = p1_total + p2_total + p3_total + p4_total;
    bonus_marks = bef_amount * (selected_val / 100);
    $('#modal-bonus-marks').val(Number(bonus_marks.toFixed(2))).prop("readonly", true);
    $('#form-total-marks').val(Number((bef_amount+bonus_marks).toFixed(2))).prop("readonly", true);

}

function formSubmit(){
    $('#result-form').submit();
}

function addManualResult(cbse_no) {
    console.log(cbse_no)
    $("#modal-cbse-no").val(cbse_no)
    $('#res_p1_w').val(0);
    $('#res_p1_p').val(0);
    $('#res_p1_t').val(0);
    $('#res_p2_w').val(0);
    $('#res_p2_p').val(0);
    $('#res_p2_t').val(0);
    $('#res_p3_w').val(0);
    $('#res_p4_w').val(0);
    $('#res_p4_p').val(0);
    $('#res_p4_t').val(0);
    $('#modal-bonus-marks').val(0).prop("readonly", true);
    $('#form-total-marks').val(0).prop("readonly", true);
    

    $('#res_p1_p').on('blur', function() {
        calculateTotalMarks()
    });
    $('#res_p1_t').on('blur', function() {
        calculateTotalMarks()
    });
    $('#res_p2_w').on('blur', function() {
        calculateTotalMarks()
    });
    $('#res_p2_p').on('blur', function() {
        calculateTotalMarks()
    });
    $('#res_p2_t').on('blur', function() {
        calculateTotalMarks()
    });
    $('#res_p3_w').on('blur', function() {
        calculateTotalMarks()
    });
    $('#res_p4_w').on('blur', function() {
        calculateTotalMarks()
    });
    $('#res_p4_p').on('blur', function() {
        calculateTotalMarks()
    });
    $('#res_p4_t').on('blur', function() {
        calculateTotalMarks()
    });
}   