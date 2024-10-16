
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

var titleToNumber = function(columnTitle) {
    let result = 0;
    let length = columnTitle.length;
    for(let i = 0; i < length; i++){
        result += (columnTitle.charCodeAt(i) - 64) * Math.pow(26, length - (i + 1));
    }
    return result;
};

var convertToTitle = function (columnNumber) {

    const Letter = "ZABCDEFGHIJKLMNOPQRSTUVWXY"
    let str = ""
    while (columnNumber > 0) {
        str = Letter.charAt(columnNumber % 26) + str
        columnNumber -= columnNumber % 26 == 0 ? 26 : columnNumber % 26
        columnNumber /= 26
    }
    return str
};

function returnNext(input) {
    number = titleToNumber(input);
    return convertToTitle(number+1);
}

$(document).ready(function() {
    drillStart = "";
    drillStartNextClmn = "";
    drillEnd = "";
    drillEndNextClmn = "";
    wtStart = "";
    wtStartNextClmn = "";
    wtEnd = "";
    wtEndNextClmn = "";
    miscStart = "";
    miscStartNextClmn = "";
    miscEnd = "";
    miscEndNextClmn = "";
    stcStart = "";
    stcStartNextClmn = "";
    stcEnd = "";
    stcEndNextClmn = "";
    $("#drill-cell-start-id").on("change", function(event) {
        inp = event.target.value;
        drillStart = titleToNumber(inp);
        drillStartNextClmn = returnNext(inp);
    });
    $("#drill-cell-end-id").on("change", function(event) {
        inp = event.target.value;
        drillEnd = titleToNumber(inp)
        if(drillEnd <= drillStart) {
            alert(`Input Column must be greater than previous value. Should be greater or equal to ${drillStartNextClmn}`);
            $(this).val("");
        }
        drillEndNextClmn = returnNext(inp)
    });
    $("#wt-cell-start-id").on("change", function(event) {
        inp = event.target.value;
        wtStart = titleToNumber(inp);
        if (wtStart <= drillEnd) {
            alert(`Input Column must be greater than previous value. Should be equal to ${drillEndNextClmn}`);
            $(this).val("");
        } else if(wtStart - drillEnd > 1) {
            alert(`Missing Column. Should be equal to ${drillEndNextClmn}`);
            $(this).val("");
        }
        wtStartNextClmn = returnNext(inp);
    });
    $("#wt-cell-end-id").on("change", function(event) {
        inp = event.target.value;
        wtEnd = titleToNumber(inp)
        if(wtEnd <= wtStart) {
            alert(`Input Column must be greater than previous value. Should be greater or equal to ${wtStartNextClmn}`);
            $(this).val("");
        }
        wtEndNextClmn = returnNext(inp)
    });
    $("#misc-cell-start-id").on("change", function(event) {
        inp = event.target.value;
        miscStart = titleToNumber(inp);
        if (miscStart <= wtEnd) {
            alert(`Input Column must be greater than previous value. Should be equal to ${wtEndNextClmn}`);
            $(this).val("");
        } else if(miscStart - wtEnd > 1) {
            alert(`Missing Column. Should be equal to ${wtEndNextClmn}`);
            $(this).val("");
        }
        miscStartNextClmn = returnNext(inp);
    });
    $("#misc-cell-end-id").on("change", function(event) {
        inp = event.target.value;
        miscEnd = titleToNumber(inp)
        if(miscEnd <= miscStart) {
            alert(`Input Column must be greater than previous value. Should be greater or equal to ${miscStartNextClmn}`);
            $(this).val("");
        }
        miscEndNextClmn = returnNext(inp)
    });
    $("#stc-cell-start-id").on("change", function(event) {
        inp = event.target.value;
        stcStart = titleToNumber(inp);
        if (stcStart <= miscEnd) {
            alert(`Input Column must be greater than previous value. Should be equal to ${miscEndNextClmn}`);
            $(this).val("");
        } else if(stcStart - miscEnd > 1) {
            alert(`Missing Column. Should be equal to ${miscEndNextClmn}`);
            $(this).val("");
        }
        stcStartNextClmn = returnNext(inp);
    });
    $("#stc-cell-end-id").on("change", function(event) {
        inp = event.target.value;
        stcEnd = titleToNumber(inp)
        if(stcEnd <= stcStart) {
            alert(`Input Column must be greater than previous value. Should be greater or equal to ${stcStartNextClmn}`);
            $(this).val("");
        }
        stcEndNextClmn = returnNext(inp)
    });
});











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
