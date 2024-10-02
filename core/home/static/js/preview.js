let selectedCheckBoxes = []
const data = document.currentScript.dataset
var students_certs = JSON.parse(data.students)
current_context = ''
preview_all_index = 0;
function clearButtonClick(href) {
    console.log("Function clled")
    window.location.replace(href)
}

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
        url: "/bulk_action/",
        data: { checkedBoxes: selectedCheckBoxes, action, csrfmiddlewaretoken: csrf_token, page},
        complete: function(data) {
            if(page==='cert'){
                window.location.href="/Preview Certificates/"+current_page+"/"
            } else {
                window.location.href="/Preview Admit Card/"+current_page+"/"
            }
        }
      });
    $(".checkbox-main").prop('checked', false);
    $(".sub-cbeckbox").prop('checked', false);
}

function openModalOnClick(index, cbse_no, page, current_page){
    current_context = "vs"
    $("#preview_next_button").hide()
    $("#preview_prev_button").hide()
    $("#preview_back_button").hide()
    $("#student-submit-button").hide()
    $("#preview_modify_button").show()
    $("#form-container").hide()
    $("#admit-card-approval-form").show()
    $("#admit-card-send-approval-form").show()
    $(".view-single-reject-form").show()
    $(".view-all-reject-form").hide()
    if(page === 'cert') {
        $("#admit-card-approval-form").attr("action", "/approve_certificate/"+cbse_no+"/"+current_page.toString()+'/')
        $("#admit-card-send-approval-form").attr("action", "/approve_certificate/"+cbse_no+"/"+current_page.toString()+'/')
        $(".view-single-reject-form").attr("action", "/reject_certificate/"+cbse_no+"/"+current_page.toString()+'/')
    } else {
        $("#admit-card-approval-form").attr("action", "/approve_admit_card/"+cbse_no+"/"+current_page.toString()+'/')
        $("#admit-card-send-approval-form").attr("action", "/send_for_approval/"+cbse_no+"/"+current_page.toString()+'/')
        $(".view-single-reject-form").attr("action", "/reject_admit_card/"+cbse_no+"/"+current_page.toString()+'/')
    }
    image_data = get_image_data(cbse_no, page)
    image_data.then(function(data) {
        $(".admit-card-image").attr("src", "data:image/png;base64,"+data.data.image)
    }).catch(function(data) {
        $(".card-container").html("<div><center>Not found</center></div>")
    })
    // console.log(students_certs)
    student_object = students_certs.filter(function (element) {
        element = element.replaceAll("'", '"').replace(' <ImageFieldFile: ', '"').replaceAll(">", '"').replaceAll("True", "true").replaceAll(": False", ": false").replaceAll("None", "null")
        element = JSON.parse(element)
        return element.CBSE_No === cbse_no
    })
    student_object = student_object[0].replaceAll("'", '"').replace(' <ImageFieldFile: ', '"').replaceAll(">", '"').replaceAll("True", "true").replaceAll(": False", ": false").replaceAll("None", "null")
    student_object = JSON.parse(student_object)
    set_form_data(student_object);
}

function get_image_data(cbse_no, type) {
    console.log("URL to call:", `/get-admit-card/${type}/${cbse_no}`)
    var ax = $.ajax({
        type: "GET",
        url: `/get-admit-card/${type}/${cbse_no}`,
        async: false,
    });
    return ax
}

function view_all_reject_button(page, current_page) {
    student_object = students_certs[preview_all_index].replaceAll("'", '"').replace(' <ImageFieldFile: ', '"').replaceAll(">", '"').replaceAll("True", "true").replaceAll(": False", ": false").replaceAll("None", "null")
    student_object = JSON.parse(student_object)
    url_to_call = null;
    if (page === 'cert'){
        url_to_call = `/reject_certificate/${student_object['CBSE_No']}/${current_page.toString()}/`
    } else {
        url_to_call = `/reject_admit_card/${student_object['CBSE_No']}/${current_page.toString()}/`
    }
    console.log("CAlling url", url_to_call)
    $.ajax({
        type: "POST",
        url: url_to_call,
        data: $(".view-all-reject-form").serialize(),
        dataType: "json",
        complete: function(data) {
            students_certs.splice(preview_all_index, 1)
            $("#rejection-reason-va").val("")
            $("#reject-btn-va").prop('disabled', true)
            view_all_function(page, current_page);
        },
        error: function(xhr, status, error) {
          // Handle error
        }
      });
}

function view_all_function(page, current_page) {
    current_context = 'va'
    // console.log(students_certs)
    $("#preview_modify_button").show()
    $("#preview_back_button").hide()
    $("#student-submit-button").hide()
    $("#form-container").hide()
    $("#image-container").show()
    $("#preview_prev_button").show()
    $("#preview_next_button").show()
    $("#admit-card-approval-form").hide()
    $("#admit-card-send-approval-form").hide()
    $(".view-single-reject-form").hide()
    $(".view-all-reject-form").show()
    if (students_certs.length > 0){
    student_object = students_certs[preview_all_index].replaceAll("'", '"').replace(' <ImageFieldFile: ', '"').replaceAll(">", '"').replaceAll("True", "true").replaceAll(": False", ": false").replaceAll("None", "null")
    student_object = JSON.parse(student_object)
    console.log(preview_all_index, students_certs)
    if (preview_all_index <= 0) {
        $("#preview_prev_button").hide();
    }else{
        $("#preview_prev_button").show();
    }
    if(preview_all_index >= students_certs.length-1) {
        $("#preview_next_button").hide();
    } else {
        $("#preview_next_button").show();
    }
    if(page === 'cert') {
        $("#admit-card-approval-form").attr("action", "/approve_certificate/"+student_object['CBSE_No']+"/"+current_page.toString()+'/')
        $("#admit-card-send-approval-form").attr("action", "/approve_certificate/"+student_object['CBSE_No']+"/"+current_page.toString()+'/')
        $(".view-single-reject-form").attr("action", "/reject_certificate/"+student_object['CBSE_No']+"/"+current_page.toString()+'/')
    } else {
        $("#admit-card-approval-form").attr("action", "/approve_admit_card/"+student_object['CBSE_No']+"/"+current_page.toString()+'/')
        $("#admit-card-send-approval-form").attr("action", "/send_for_approval/"+student_object['CBSE_No']+"/"+current_page.toString()+'/')
        $(".view-single-reject-form").attr("action", "/reject_admit_card/"+student_object['CBSE_No']+"/"+current_page.toString()+'/')
    }
    image = get_image_data(student_object['CBSE_No'], page)
    image.then(function(data) {
        try {
            if(data.status==200){
                $(".card-container").html(`<center><img src='data:image/png;base64,${data.data.image}' alt='Certificate' class='admit-card-image'></center>`)
            } else{
                $(".card-container").html("<div><center>Not found</center></div>")
            }
            
        } catch (error) {
            $(".card-container").html("<div><center>Not found</center></div>")
        }
    }).catch(function(data) {
        console.log(data)
        $(".card-container").html("<div><center>Not found</center></div>")
    })
    set_form_data(student_object);
    }else{
        $("#preview_prev_button").hide()
        $("#preview_next_button").hide()
        $(".view-all-reject-form").hide()
        $(".card-container").html("<div><center>Not found</center></div>")
    }
}

function set_form_data(student_object) {
    $('#student-id').val(student_object["id"]);
    $('#student-image').attr('src', '/media/'+student_object['Photo'])
    $('#modal-student-name').html(student_object["Name"]);
    $('#modal-cbse-no').val(student_object["CBSE_No"]);
    $('#modal-full-name').val(student_object["Name"]);
    $('#modal-full-name-hindi').val(student_object["name_hindi"]);
    $('#modal-father-name').val(student_object["Fathers_Name"]);
    $('#modal-father-name-hindi').val(student_object["fathers_name_hindi"]);
    $('#modal-dob').val(student_object["DOB"]);
    $('#modal-address').html(student_object["Home_Address"]);
    $('#modal-unit').val(student_object["Unit"]);
    $('#modal-rank').val(student_object["Rank"]);
    $('#modal-yopb-cert').val(student_object["Year_of_passing_B_Certificate"]);
    $('#modal-fresh-failure').val(student_object["Fresh_Failure"]);
    $('#modal-school').html(student_object["School_College_Class"]);
    $('#modal-1st-year').val(student_object["Attendance_1st_year"]);
    $('#modal-2nd-year').val(student_object["Attendance_2nd_year"]);
    $('#modal-3rd-year').val(student_object["Attendance_3rd_year"]);
    $('#modal-camp-name').val(student_object["Name_of_camp_attended_1"]);
    $('#modal-camp-date').val(student_object["Date_camp_1"]);
    $('#modal-camp-location').html(student_object["Location_camp_1"]);
    $('#modal-camp-name-2').val(student_object["Name_of_camp_attended_2"]);
    $('#modal-camp-date-2').val(student_object["Date_camp_2"]);
    $('#modal-camp-location-2').html(student_object["Location_camp_2"]);
}

function nextButtonClick(page, current_page) {
    preview_all_index ++;
    $(".modal").scrollTop()
    view_all_function(page, current_page);
}

function prevButtonClick(page, current_page) {
    preview_all_index --;
    view_all_function(page, current_page);
}

function modifyButtonClick() {
    $("#preview_modify_button").hide()
    $("#preview_back_button").show()
    $("#student-submit-button").show()
    $("#form-container").show()
    $("#image-container").hide()
    $("#preview_prev_button").hide()
    $("#preview_next_button").hide()
    $("#admit-card-approval-form").hide()
    $("#admit-card-send-approval-form").hide()
    $("#admit-card-reject-form").hide()
}

function backButtonClick() {
    $("#preview_modify_button").show()
    $("#preview_back_button").hide()
    $("#student-submit-button").hide()
    $("#form-container").hide()
    $("#image-container").show()
    if (preview_all_index <= 0 || current_context==='vs') {
        $("#preview_prev_button").hide();
    }else{
        $("#preview_prev_button").show();
    }
    if(preview_all_index >= students_certs.length-1 || current_context==='vs') {
        $("#preview_next_button").hide();
    } else {
        $("#preview_next_button").show();
    }
}

function studentDetailFormSubmit(page, current_page) {
    console.log("called")
    formdata = new FormData($("#student-detail-form")[0])
    $.ajax({
        type: "POST",
        url: "/update/"+current_page+"/",
        data: $("#student-detail-form").serialize(),
        dataType: "json",
        complete: function(data) {
            json = {}
            formdata.forEach(function(value ,key) {
                json[key] = value
            })
            json["name_hindi"] = json["Name_Hindi"]
            json["fathers_name_hindi"] = json["Fathers_Name_Hindi"]
            json["Photo"] = JSON.parse( students_certs[preview_all_index].replaceAll("'", '"').replace(' <ImageFieldFile: ', '"').replaceAll(">", '"').replaceAll("True", "true").replaceAll(": False", ": false").replaceAll("None", "null"))["Photo"]
            students_certs[preview_all_index] = JSON.stringify(json)
            view_all_function(page, current_page);
            
        },
        error: function(xhr, status, error) {
          // Handle error
        }
      });
}