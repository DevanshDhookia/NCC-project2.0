const data = document.currentScript.dataset
students_result = JSON.parse(data["result"])

function dataToJson(data) {
    return JSON.parse(data.replaceAll("'", '"').replace(' <ImageFieldFile: ', '"').replaceAll(">", '"').replaceAll("True", "true").replaceAll(": False", ": false").replaceAll("None", "null"))
}

function formSubmit(){
    $('#result-form').submit();
}

function calculateTotalMarks(){
    selected_val = Number($('#bonus_marks_cat').find(":selected").attr("percentage"));
    bef_amount = Number($('#res_p1_w').val())+
    Number($('#res_p1_p').val())+
    Number($('#res_p1_t').val())+
    Number($('#res_p2_w').val())+
    Number($('#res_p2_p').val())+
    Number($('#res_p2_t').val())+
    Number($('#res_p3_w').val())+
    Number($('#res_p4_w').val())+
    Number($('#res_p4_p').val())+
    Number($('#res_p4_t').val());
    bonus_marks = bef_amount * (selected_val / 100);
    $('#modal-bonus-marks').val(bonus_marks).prop("readonly", true);
    $('#form-total-marks').val(bef_amount+bonus_marks).prop("readonly", true);

}

function openModalOnClick(index, event_type) {
    student_object = students_result[Number(index)-1];
    $('#student-id').val(student_object["id"]);
    $('#modal-student-name').html(student_object["student_name"]);
    $('#modal-cbse-no').val(student_object["student_id"]);
    $('#modal-full-name').val(student_object["student_name"]).prop("readonly", true);
    $('#modal-unit').val(student_object["unit"]).prop("readonly", true);
    $('#modal-rank').val(student_object["rank"]).prop("readonly", true);
    $('#modal-fresh-failure').val(student_object["result"]["Pass_Fail"]).prop("readonly", event_type === 'view' ? true : false);
    $('#modal-attandance').val(student_object["result"]["Parade_attendance"]).prop("readonly", event_type === 'view' ? true : false);
    $('#modal-school').html(student_object["college"]).prop("readonly", true);
    $('#res_p1_w').val(student_object["result"]["Paper1_W"]).prop("readonly", event_type === 'view' ? true : false);
    $('#res_p1_p').val(student_object["result"]["Paper1_P"]).prop("readonly", event_type === 'view' ? true : false);
    $('#res_p1_t').val(student_object["result"]["Paper1_T"]).prop("readonly", event_type === 'view' ? true : false);
    $('#res_p2_w').val(student_object["result"]["Paper2_W"]).prop("readonly", event_type === 'view' ? true : false);
    $('#res_p2_p').val(student_object["result"]["Paper2_P"]).prop("readonly", event_type === 'view' ? true : false);
    $('#res_p2_t').val(student_object["result"]["Paper2_T"]).prop("readonly", event_type === 'view' ? true : false);
    $('#res_p3_w').val(student_object["result"]["Paper3_W"]).prop("readonly", event_type === 'view' ? true : false);
    $('#res_p4_w').val(student_object["result"]["Paper4_W"]).prop("readonly", event_type === 'view' ? true : false);
    $('#res_p4_p').val(student_object["result"]["Paper4_P"]).prop("readonly", event_type === 'view' ? true : false);
    $('#res_p4_t').val(student_object["result"]["Paper4_T"]).prop("readonly", event_type === 'view' ? true : false);
    $('#modal-bonus-marks').val(student_object["result"]["Bonus_marks"]).prop("readonly", true);
    $('#form-total-marks').val(student_object["result"]["Final_total"]).prop("readonly", true);
    if(event_type === 'view'){
        $('#student-submit-button').hide()
        $('#student-approval-button').hide()
        $('#bonus_marks_cat').val(student_object["result"]["bonus_marks_cat"]).attr("disabled", "disabled");
    } else {
        $('#student-submit-button').show()
        $('#student-approval-button').show()
        $('#bonus_marks_cat').val(student_object["result"]["bonus_marks_cat"]).removeAttr("disabled");
    }
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
