let selectedCheckBoxes = []
const data = document.currentScript.dataset
students_certs = JSON.parse(data.students)
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
    $("#preview_next_button").hide()
    $("#preview_prev_button").hide()
    if(page === 'cert') {
        $("#admit-card-approval-form").attr("action", "/approve_certificate/"+cbse_no+"/"+current_page.toString()+'/')
        $("#admit-card-send-approval-form").attr("action", "/approve_certificate/"+cbse_no+"/"+current_page.toString()+'/')
        $("#admit-card-reject-form").attr("action", "/reject_certificate/"+cbse_no+"/"+current_page.toString()+'/')
    } else {
        $("#admit-card-approval-form").attr("action", "/approve_admit_card/"+cbse_no+"/"+current_page.toString()+'/')
        $("#admit-card-send-approval-form").attr("action", "/send_for_approval/"+cbse_no+"/"+current_page.toString()+'/')
        $("#admit-card-reject-form").attr("action", "/reject_admit_card/"+cbse_no+"/"+current_page.toString()+'/')
    }
    image_data = get_image_data(cbse_no, page)
    image_data.then(function(data) {
        $(".admit-card-image").attr("src", "data:image/png;base64,"+data.data.image)
    }).catch(function(data) {
        $(".card-container").html("<div><center>Not found</center></div>")
    })
}

function get_image_data(cbse_no, type) {
    var ax = $.ajax({
        type: "GET",
        url: `/get-admit-card/${type}/${cbse_no}`,
        async: false,
    });
    return ax
}

function view_all_function(page, current_page) {
    console.log(preview_all_index === 0, preview_all_index === students_certs.length-1 )
    if (preview_all_index === 0) {
        $("#preview_prev_button").hide();
    }else{
        $("#preview_prev_button").show();
    }
    if(preview_all_index === students_certs.length-1) {
        $("#preview_next_button").hide();
    } else {
        $("#preview_next_button").show();
    }
    if(page === 'cert') {
        $("#admit-card-approval-form").attr("action", "/approve_certificate/"+students_certs[preview_all_index]+"/"+current_page.toString()+'/')
        $("#admit-card-send-approval-form").attr("action", "/approve_certificate/"+students_certs[preview_all_index]+"/"+current_page.toString()+'/')
        $("#admit-card-reject-form").attr("action", "/reject_certificate/"+students_certs[preview_all_index]+"/"+current_page.toString()+'/')
    } else {
        $("#admit-card-approval-form").attr("action", "/approve_admit_card/"+students_certs[preview_all_index]+"/"+current_page.toString()+'/')
        $("#admit-card-send-approval-form").attr("action", "/send_for_approval/"+students_certs[preview_all_index]+"/"+current_page.toString()+'/')
        $("#admit-card-reject-form").attr("action", "/reject_admit_card/"+students_certs[preview_all_index]+"/"+current_page.toString()+'/')
    }
    image = get_image_data(students_certs[preview_all_index], page)
    image.then(function(data) {
        $(".admit-card-image").attr("src", "data:image/png;base64,"+data.data.image)
    }).catch(function(data) {
        $(".card-container").html("<div><center>Not found</center></div>")
    })
}

function nextButtonClick(page, current_page) {
    preview_all_index ++;
    view_all_function(page, current_page);
}

function prevButtonClick(page, current_page) {
    preview_all_index --;
    view_all_function(page, current_page);
}