const data = document.currentScript.dataset
students_result = JSON.parse(data["result"])

function dataToJson(data) {
    return JSON.parse(data.replaceAll("'", '"').replace(' <ImageFieldFile: ', '"').replaceAll(">", '"').replaceAll("True", "true").replaceAll(": False", ": false").replaceAll("None", "null"))
}

function openModalOnClick(index, event_type) {
    student_object = students_result[Number(index)-1];
    console.log(student_object)
    $('#student-id').val(student_object["id"]);
    $('#modal-student-name').html(student_object["student_name"]);
    $('#modal-cbse-no').val(student_object["student_id"]);
    $('#modal-full-name').val(student_object["student_name"]).prop("readonly", event_type === 'view' ? true : false);
    $('#modal-unit').val(student_object["unit"]).prop("readonly", event_type === 'view' ? true : false);
    $('#modal-rank').val(student_object["rank"]).prop("readonly", event_type === 'view' ? true : false);
    $('#modal-fresh-failure').val(student_object["result"]["Pass_Fail"]).prop("readonly", event_type === 'view' ? true : false);
    $('#modal-school').html(student_object["college"]).prop("readonly", event_type === 'view' ? true : false);
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
    if(event_type === 'view'){
        $('#student-submit-button').hide()
    } else {
        $('#student-submit-button').show()
    }
}
