let selectedCheckBoxes = []
const data = document.currentScript.dataset
students_certs = JSON.parse(data.students)


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

function bulk_action(action, csrf_token, page) {
    $.ajax({
        type: "POST",
        url: "/bulk_action/",
        data: { checkedBoxes: selectedCheckBoxes, action, csrfmiddlewaretoken: csrf_token, page},
        complete: function(data) {
            if(page==='cert'){
                window.location.href="/Preview Certificates/"
            } else {
                window.location.href="/Preview Admit Card/"
            }
        }
      });
    $(".checkbox-main").prop('checked', false);
    $(".sub-cbeckbox").prop('checked', false);
}

function openModalOnClick(index, cbse_no, page){
    $(".admit-card-image").attr("src", "data:image/png;base64,"+students_certs[index-1])
    if(page === 'cert') {
        $("#admit-card-approval-form").attr("action", "/approve_certificate/"+cbse_no+"/")
        $("#admit-card-send-approval-form").attr("action", "/approve_certificate/"+cbse_no+"/")
        $("#admit-card-reject-form").attr("action", "/reject_certificate/"+cbse_no+"/")
    } else {
        $("#admit-card-approval-form").attr("action", "/approve_admit_card/"+cbse_no+"/")
        $("#admit-card-send-approval-form").attr("action", "/send_for_approval/"+cbse_no+"/")
        $("#admit-card-reject-form").attr("action", "/reject_admit_card/"+cbse_no+"/")
    }
}