const data = document.currentScript.dataset
students = JSON.parse(data.students)

function clearButtonClick() {
    console.log("Function clled")
    window.location.replace('/Student Details/')
}


function studentDetailFormSubmit(e) {
    console.log("called")
    $('#student-detail-form').submit();
  }


function openModalOnClick(index, event_type) {
    console.log(Number(index))
    st = students[index-1].replaceAll("'", '"').replace(' <ImageFieldFile: ', '"').replaceAll(">", '"').replaceAll("True", "true").replaceAll(": False", ": false").replaceAll("None", "null")
    student_object = JSON.parse(st);
    console.log(student_object)
    $('#student-id').val(student_object["id"]);
    $('#student-image').attr('src', '/media/'+student_object['Photo'])
    $('#modal-student-name').html(student_object["Name"]);
    $('#modal-cbse-no').val(student_object["CBSE_No"]);
    $('#modal-full-name').val(student_object["Name"]).prop("readonly", event_type === 'view' ? true : false);
    $('#modal-father-name').val(student_object["Fathers_Name"]).prop("readonly", event_type === 'view' ? true : false);
    $('#modal-dob').val(student_object["DOB"]).prop("readonly", event_type === 'view' ? true : false);
    $('#modal-address').html(student_object["Home_Address"]).prop("readonly", event_type === 'view' ? true : false);
    $('#modal-unit').val(student_object["Unit"]).prop("readonly", event_type === 'view' ? true : false);
    $('#modal-rank').val(student_object["Rank"]).prop("readonly", event_type === 'view' ? true : false);
    $('#modal-yopb-cert').val(student_object["Year_of_passing_B_Certificate"]).prop("readonly", event_type === 'view' ? true : false);
    $('#modal-fresh-failure').val(student_object["Fresh_Failure"]).prop("readonly", event_type === 'view' ? true : false);
    $('#modal-school').html(student_object["School_College_Class"]).prop("readonly", event_type === 'view' ? true : false);
    $('#modal-1st-year').val(student_object["Attendance_1st_year"]).prop("readonly", event_type === 'view' ? true : false);
    $('#modal-2nd-year').val(student_object["Attendance_2nd_year"]).prop("readonly", event_type === 'view' ? true : false);
    $('#modal-3rd-year').val(student_object["Attendance_3rd_year"]).prop("readonly", event_type === 'view' ? true : false);
    $('#modal-camp-name').val(student_object["Name_of_camp_attended_1"]).prop("readonly", event_type === 'view' ? true : false);
    $('#modal-camp-date').val(student_object["Date_camp_1"]).prop("readonly", event_type === 'view' ? true : false);
    $('#modal-camp-location').html(student_object["Location_camp_1"]).prop("readonly", event_type === 'view' ? true : false);
    $('#modal-camp-name-2').val(student_object["Name_of_camp_attended_2"]).prop("readonly", event_type === 'view' ? true : false);
    $('#modal-camp-date-2').val(student_object["Date_camp_2"]).prop("readonly", event_type === 'view' ? true : false);
    $('#modal-camp-location-2').html(student_object["Location_camp_2"]).prop("readonly", event_type === 'view' ? true : false);
    if(event_type === 'view'){
        $('#student-submit-button').hide()
    } else {
        $('#student-submit-button').show()
    }
}