const data = document.currentScript.dataset
students_result = JSON.parse(data["result"])
let selectedCheckBoxes = []


function onMainCheckboxToggle() {
    checked = $(".checkbox-main").prop('checked');
    $(".sub-checkbox").prop("checked", checked)
    checkboxes = $(".sub-checkbox");
    if(checked) {
        for(i = 0; i < checkboxes.length; i++) {
            selectedCheckBoxes.push(checkboxes[i].value)
        }
        selectedCheckBoxes = [...new Set(selectedCheckBoxes)]
    } else {
        selectedCheckBoxes = []
    }
    display_bulk_form()
}

function onSubCheckboxToggle(value1, value) {
    console.log(value, value1);
    $(".checkbox-main").prop("checked", false)
    if($(".sub-checkbox-"+value1).prop('checked')){
        selectedCheckBoxes.push(value)
    } else {
        selectedCheckBoxes = selectedCheckBoxes.filter((element) => element !== value)
    }
    display_bulk_form()
}

function display_bulk_form() {
    if (selectedCheckBoxes.length === 0) {
        $("#bulk-approve-form").prop("hidden", true)
    } else {
        $("#bulk-approve-form").prop("hidden", false)
    }
}

function bulk_action(action, csrf_token, page, current_page) {
    
    $.ajax({
        type: "POST",
        url: "/generate_all_certs/",
        data: { checkedBoxes: selectedCheckBoxes, action, csrfmiddlewaretoken: csrf_token, page},
        complete: function(data) {
        window.location.href="/view-results/"+current_page+"/"
        }
      });
    $(".checkbox-main").prop('checked', false);
    $(".sub-cbeckbox").prop('checked', false);
}



function clearButtonClick(href) {
    console.log("Function clled")
    window.location.replace(href)
}

function dataToJson(data) {
    return JSON.parse(data.replaceAll("'", '"').replace(' <ImageFieldFile: ', '"').replaceAll(">", '"').replaceAll("True", "true").replaceAll(": False", ": false").replaceAll("None", "null"))
}

function formSubmit(){
    $('#result-form').submit();
}

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

function openModalOnClick(index, event_type) {
    student_object = students_result[Number(index)-1];
    $('#student-id').val(student_object["id"]);
    $('#modal-student-name').html(student_object["student_name"]);
    $('#modal-cbse-no').val(student_object["student_id"]);
    $('#modal-full-name').val(student_object["student_name"]).prop("readonly", true);
    $('#modal-unit').val(student_object["unit"]).prop("readonly", true);
    $('#modal-rank').val(student_object["rank"]).prop("readonly", true);
    $('#modal-grade').val(student_object["result"]["Grade"]).prop("readonly", event_type === 'view' ? true : false);
    $('#modal-attandance').val(student_object["result"]["Parade_attendance"]).prop("readonly", event_type === 'view' ? true : false);
    $('#modal-school').html(student_object["college"]).prop("readonly", true);
    $('#res_p1_w').val(student_object["result"]["Paper1_W"]).prop("readonly", true);
    $('#res_p1_p').val(student_object["result"]["Paper1_P"]).prop("readonly", event_type === 'view' ? true : false);
    $('#res_p1_t').val(student_object["result"]["Paper1_T"]).prop("readonly", true);
    $('#res_p2_w').val(student_object["result"]["Paper2_W"]).prop("readonly", true);
    $('#res_p2_p').val(student_object["result"]["Paper2_P"]).prop("readonly", event_type === 'view' ? true : false);
    $('#res_p2_t').val(student_object["result"]["Paper2_T"]).prop("readonly", true);
    $('#res_p3_w').val(student_object["result"]["Paper3_W"]).prop("readonly", true);
    $('#res_p4_w').val(student_object["result"]["Paper4_W"]).prop("readonly", true);
    $('#res_p4_p').val(student_object["result"]["Paper4_P"]).prop("readonly", event_type === 'view' ? true : false);
    $('#res_p4_t').val(student_object["result"]["Paper4_T"]).prop("readonly", true);
    $('#modal-bonus-marks').val(student_object["result"]["Bonus_marks"]).prop("readonly", true);
    $('#form-total-marks').val(student_object["result"]["Final_total"]).prop("readonly", true);
    console.log(student_object["result"], typeof(student_object["result"]['Pass']));
    if(event_type === 'view'){
        $('#student-submit-button').hide()
        // $('#student-approval-button').hide()
        $('#modal-fresh-failure').val(student_object["result"]["Pass"] ? 'true' : 'false').attr("disabled", "disabled");
        $('#bonus_marks_cat').val(student_object["result"]["bonus_marks_cat"]).attr("disabled", "disabled");
    } else {
        $('#student-submit-button').show()
        // $('#student-approval-button').show()
        // $('#student-approval-button').attr('href', '/generate_certificate/'+student_object["student_id"])
        if(!student_object["result"]["Pass"]) {
            $('#student-approval-button').hide()
        }
        $('#modal-fresh-failure').val(student_object["result"]["Pass"] ? 'true' : 'false').removeAttr("disabled");
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
