from django.shortcuts import render, redirect
from django.http import HttpResponseBadRequest
from django.core.files.base import ContentFile, File
from django.core.files.storage import default_storage
import os
import pandas as pd
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from django.shortcuts import get_object_or_404
from home.models import Student , Clerk , Colonel , Brigadier ,Director_General, Result, BonusMarksCategories, Certificate
from django.conf import settings
from django.urls import reverse
from django.contrib.auth import login, logout, authenticate, get_backends
from django.contrib.auth.models import User , Group
from common_utils.login_utilities import LoginValidator
from common_utils.jwt_manager import JwtUtility
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.forms.models import model_to_dict
from django.db.models import Q
import pyqrcode 
import png
from datetime import date

login_validator = LoginValidator()
jwt_utility = JwtUtility()

def home(request):
    return render(request, "Login_Page/index.html")

def contact(request):
    return render(request, "Login_Page/contact.html")

def SignIn(request):
    if request.user is None:
        return redirect('/clerk/')
    if request.method == 'POST':
        data = request.POST
        user = authenticate(username=data.get("username"), password=data.get("password"))
        if user is not None:
            token = jwt_utility.get_jwt_token({
                "username": user.username
            })
            request.user = user
            request.session["token"] = token
            login(request, user)

            return redirect("/clerk/")
        else:
            messages.info(request, "Invalid Login Credentials")
            return redirect("/SignIn/")
    return render(request, "Login_Page/SignIn.html", {"page_name": "Ludiflex | Login & Registration"})

@login_required
def register(request):
    if request.user.has_perm('home.can_create_new_users'):
        if request.method == 'POST':
            username = request.POST.get('username')
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')

            # Basic validation
            if not username or not password1 or not password2:
                messages.error(request, "All fields are required.")
                return redirect('/register/')

            if password1 != password2:
                messages.error(request, "Passwords do not match.")
                return redirect('/register/')

            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists.")
                return redirect('/register/')

            # Create new user
            user = User.objects.create_user(username=username)
            user.set_password(password1)
            user.save()

            # Determine which group and model to associate based on the logged-in user's role
            if request.user.groups.filter(name='Director_General').exists():
                group_name = 'Brigadier'
                model_class = Brigadier
                related_model = Director_General
                related_field = 'director_general'
            elif request.user.groups.filter(name='Brigadier').exists():
                group_name = 'Colonel'
                model_class = Colonel
                related_model = Brigadier
                related_field = 'brigadier'
            elif request.user.groups.filter(name='Colonel').exists():
                group_name = 'Clerk'
                model_class = Clerk
                related_model = Colonel
                related_field = 'colonel'
            else:
                messages.error(request, "You do not have permission to register users.")
                user.delete()  # Delete the user since permission failed
                return redirect('/register/')

            # Add user to the appropriate group
            group, created = Group.objects.get_or_create(name=group_name)
            user.groups.add(group)

            # Get the related instance (e.g., Director_General for Brigadier)
            related_instance = related_model.objects.get(user=request.user)

            # Create the corresponding model instance but don't save it yet
            model_instance = model_class(user=user)

            # Set the relationship field before saving
            setattr(model_instance, related_field, related_instance)
            model_instance.save()

            messages.success(request, f"{group_name} registered successfully.")
            return redirect('/register/')

        return render(request, "Login_Page/register.html")
    else:
        return redirect("/index/")

def user_logout(request):
    request.session.delete("token")
    request.session.flush()
    logout(request)
    return redirect("/SignIn/")

#-------------- Home Page Views -------------#
def index(request):
    return render(request, "Login_Page/index.html")

@login_required
def clerk_page(request):
    if login_validator.is_user_logged_in(request) and request.user.is_authenticated:
        admitcard_generated_students = 0
        send_for_approval_students = 0
        reject_admit_card_students = 0

        for student in Student.objects.all():
            if student.admit_card_generated:
                admitcard_generated_students += 1
            if student.sent_for_approval:
                send_for_approval_students += 1
            if student.rejection_reason:  # This checks if rejection_reason is not None and not an empty string
                reject_admit_card_students += 1

        context = {
            'total_students': Student.objects.all(),
            'admitcard_generated_students': admitcard_generated_students,
            'send_for_approval_students': send_for_approval_students,
            'reject_admit_card_students': reject_admit_card_students,
        }

        return render(request, "clerk/clerk.html", context)
    else:
        return redirect("/SignIn/")
@login_required
def Add_Result(request):
    return render(request, "clerk/Add_Result.html")

def add_result_data(request):
    if request.method == 'POST':
        request_data = request.POST
        type = request_data.get('type')
        if type == 'manual':
            cbse_no = request_data.get("CBSE_No")
            result_pf = request_data.get("Fresh_Failure")
            attand = request_data.get("attandance")
            grade = request_data.get("grade")
            p1_w = request_data.get("result_p1_w")
            p1_p = request_data.get("result_p1_p")
            p1_t = request_data.get("result_p1_t")
            p2_w = request_data.get("result_p2_w")
            p2_p = request_data.get("result_p2_p")
            p2_t = request_data.get("result_p2_t")
            p3_w = request_data.get("result_p3_w")
            p4_w = request_data.get("result_p4_w")
            p4_p = request_data.get("result_p4_p")
            p4_t = request_data.get("result_p4_t")
            bonus_cat = request_data.get("bonus_marks_cat")
            bonus_marks = request_data.get("bonus_marks")
            total = request_data.get("modal_total")
            result = Result.objects.create(
                Parade_attendance = attand,
                Paper1_W = p1_w,
                Paper1_P = p1_p,
                Paper1_T = p1_t,
                Paper2_W = p2_w,
                Paper2_P = p2_p,
                Paper2_T = p2_t,
                Paper3_W = p3_w,
                Paper4_W = p4_w,
                Paper4_P = p4_p,
                Paper4_T = p4_t,
                bonus_marks_cat = BonusMarksCategories.objects.get(id=bonus_cat),
                Bonus_marks = bonus_marks,
                Final_total = total,
                Pass = True if result_pf == 'true' else False,
                Grade = grade,
            )
            student = Student.objects.get(CBSE_No=cbse_no)
            student.result = result
            student.save()
            messages.info(request, "Result data added successfully")
            return redirect("/Add Result/")
        elif type == 'upload':
            pass
    elif request.method == 'GET':
        request_data = request.GET
        student = Student.objects.filter(CBSE_No=request_data.get('cbse_no')).first()
        data = None
        bonus_marks_cat = None
        if student:
            data = { "status": "true", "id": student.id, "cbse_no": student.CBSE_No, "name": student.Name, "unit": student.Unit, "rank": student.Rank }
            bonus_marks_cat = BonusMarksCategories.objects.all()
            if student.result != None:
                messages.info(request, "Student result already available")
                return redirect("/Add Result/")
        else:
            messages.info(request, "CBSE No. does not exists.")
            return redirect("/Add Result/")
        return render(request, "clerk/Add_Result.html", context={"student": data,"bonus_marks": bonus_marks_cat})

@login_required
def results(request):
    if request.user.has_perm("home.view_result"):
        results_data = None
        if request.method == 'POST' and request.user.has_perm("home.change_result"):
            request_data = request.POST
            st_id = request_data.get("id")
            student = Student.objects.filter(id=st_id).first()
            if student:
                st_result = Result.objects.filter(id=student.result.id)[0]
                st_result.Parade_attendance = request_data.get("attandance")
                st_result.Paper1_W = request_data.get("result_p1_w")
                st_result.Paper1_P = request_data.get("result_p1_p")
                st_result.Paper1_T = request_data.get("result_p1_t")
                st_result.Paper2_W = request_data.get("result_p2_w")
                st_result.Paper2_P = request_data.get("result_p2_p")
                st_result.Paper2_T = request_data.get("result_p2_t")
                st_result.Paper3_W = request_data.get("result_p3_w")
                st_result.Paper4_W = request_data.get("result_p4_w")
                st_result.Paper4_P = request_data.get("result_p4_p")
                st_result.Paper4_T = request_data.get("result_p4_t")
                st_result.bonus_marks_cat = BonusMarksCategories.objects.get(id=request_data.get("bonus_marks_cat"))
                st_result.Bonus_marks = request_data.get("bonus_marks")
                st_result.Final_total = request_data.get("modal_total")
                st_result.Pass = True if request_data.get("Fresh_Failure") == 'true' else False
                st_result.Grade = request_data.get("grade")
                st_result.save()
            else:
                return redirect("/index/")
        if request.user.groups.filter(name='Colonel').exists():
            results_data = Student.objects.filter(result__isnull=False, colonel=Colonel.objects.get(user_id=request.user.id)).order_by('id')
        elif request.user.groups.filter(name='Clerk').exists():
            results_data = Student.objects.filter(result__isnull=False, clerk=Clerk.objects.get(user_id=request.user.id)).order_by('id')
        elif request.user.groups.filter(name='Brigadier').exists():
            results_data = Student.objects.filter(result__isnull=False, brigadier=Brigadier.objects.get(user_id=request.user.id)).order_by('id')
        elif request.user.groups.filter(name='Director_General').exists():
            results_data = Student.objects.filter(result__isnull=False, director_general=Director_General.objects.get(user_id=request.user.id)).order_by('id')
        bonus_marks_cat = BonusMarksCategories.objects.all()
        bonus_marks_ser = json.dumps([model_to_dict(item) for item in bonus_marks_cat], cls=DjangoJSONEncoder)
        return_data = [{"id": student.id,"student_id": student.CBSE_No, "result": model_to_dict(student.result), "student_name": student.Name, "college": student.School_College_Class, "unit": student.Unit,"rank": student.Rank, "p_1_total": student.result.Paper1_P + student.result.Paper1_W + student.result.Paper1_T, "p_2_total": student.result.Paper2_P + student.result.Paper2_W + student.result.Paper2_T, "p_3_total": student.result.Paper3_W, "p_4_total": student.result.Paper4_P + student.result.Paper4_W + student.result.Paper4_T} for student in results_data]
        serialized_return_data = json.dumps(list(return_data), cls=DjangoJSONEncoder)
        return render(request, "clerk/view_results.html", {"result_data": return_data, "serialized_result_data": serialized_return_data, "bonus_marks": bonus_marks_cat, "bonus_marks_ser": bonus_marks_ser})
    else:
        return redirect('/index/')


@login_required
def Preview_Admit_Card(request):
    if login_validator.is_user_logged_in(request) and request.user.is_authenticated:
        # Retrieve all pending students ordered by ID
        print(request.user.id)
        pending_students = []
        if request.user.groups.filter(name='Colonel').exists():
            pending_students = Student.objects.filter(admit_card_approved=False, rejection_reason=None, admit_card_send_for_approval=True, colonel_id=Colonel.objects.filter(user_id=request.user.id)[0].id).order_by('id')
        elif request.user.groups.filter(name='Clerk').exists():
            pending_students = Student.objects.filter(admit_card_approved=False, admit_card_send_for_approval=False, clerk_id=Clerk.objects.filter(user_id=request.user.id)[0].id).order_by('id')
        else:
            messages.error(request, "You do not have permission to perform this action.")
            return redirect('/clerk/')
        if not pending_students.exists():
            # If no students are left to preview, render the "All Students Previewed" page
            return render(request, "clerk/All_Students_Previewed.html")

        # Get the current student ID from the request or default to the first pending student
        student_id = request.GET.get('student_id')
        if student_id:
            student = get_object_or_404(Student, id=student_id, admit_card_approved=False, rejection_reason=None)
        else:
            student = pending_students.first()

        # Generate the admit card if it hasn't been generated yet
        if not student.admit_card_generated:
            admit_card_image_path = generate_admit_card(student)
            student.admit_card_generated = True
            student.save()
        else:
            admit_card_image_path = os.path.join(settings.MEDIA_URL, 'Admit_Cards', f'{student.CBSE_No}_admit_card.png')

        # Get the current student's position in the list
        student_ids = list(pending_students.values_list('id', flat=True))
        current_index = student_ids.index(student.id)

        # Determine the next and previous student indices
        next_student = pending_students[current_index + 1] if current_index + 1 < len(student_ids) else None
        prev_student = pending_students[current_index - 1] if current_index - 1 >= 0 else None

        # Render the template with the appropriate context
        context = {
            'student': student,
            'admit_card_image_path': admit_card_image_path,
            'next_student': next_student,
            'prev_student': prev_student,
        }
        return render(request, "clerk/Preview_Admit_Card.html", context)
    else:
        return redirect("/SignIn/")
    
@login_required
def generate_certificate_action(request, cbse_no):
    student = Student.objects.filter(CBSE_No = cbse_no)
    print('Generating certificate for student with CBSE No: ', cbse_no)
    if student.exists():
        student = student[0]
        id = str(student.id)
        year = str(date.today().year)
        try:
            cert = Certificate.objects.create(
                certificate_id = cbse_no+"/"+student.Certificate_type + " Cert/"+student.Unit+"/"+year + "/" +id.zfill(5), 
                certificate_generated = True,
                Date = date.today(),
                Approval_stage=0,
                Generation_date = date.today(),
                Place = "Kanpur"
            )
        except Exception as error:
            error.with_traceback
            messages.error(request, "Certificate already generated for the student")
            return redirect("/view-results")
        student.certificate = cert
        student.save()
        try:
            certificate_image_path = generate_certificate(student)
            cert.certificate_path = certificate_image_path,
            student.certificate = cert
            student.save()
        except Exception as e:
            print("Unable to generate certificate", e)
            student.certificate = None
            student.save()
            cert.delete()
            messages.info(request, "Error while generating certificate")
            return redirect("/view-results/")
        messages.info(request, "Certificate Sent for Approval")
    else:
        messages.error(request, "Student not found with provided CBSE No.")
    return redirect("/view-results/")


@login_required
def Preview_Certificates(request):
     # Determine the user's role and fetch pending students accordingly
    pending_students=[]
    if request.user.groups.filter(name='Director_General').exists():
        director_general_id = Director_General.objects.get(user_id=request.user.id).id
        pending_students = Student.objects.filter(
            certificate__Approval_stage=2,
            certificate__Rejected_reason=None,
            director_general_id=director_general_id,
            certificate__certificate_generated=True
        ).order_by('id')

    elif request.user.groups.filter(name='Brigadier').exists():
        brigadier_id = Brigadier.objects.get(user_id=request.user.id).id
        pending_students = Student.objects.filter(
            certificate__Approved=False,
            certificate__Approval_stage=1,
            certificate__Rejected_reason=None,
            brigadier_id=brigadier_id,
            certificate__certificate_generated=True
        ).order_by('id')

    elif request.user.groups.filter(name='Colonel').exists():
        colonel_id = Colonel.objects.get(user_id=request.user.id).id
        pending_students = Student.objects.filter(
            certificate__Approved=False,
            certificate__Approval_stage=0,
            certificate__Rejected_reason=None,
            colonel_id=colonel_id,
            certificate__certificate_generated=True
        ).order_by('id')
    elif request.user.groups.filter(name='Clerk').exists():
        clerk_id = Clerk.objects.get(user_id=request.user.id).id
        pending_students = Student.objects.filter(
            certificate__Approved=False,
            certificate__Rejected_reason=None,
            clerk_id=clerk_id,
            certificate__certificate_generated=True
        ).order_by('id')
    else:
        messages.error(request, "You do not have permission to perform this action.")
        return redirect('/clerk/')

    # pending_students=Student.objects.all()
    # If no pending students, render the "All Students Previewed" page
    if not pending_students.exists():
        return render(request, "clerk/All_Students_Previewed.html")

    # Get the current student from request or default to the first in the list
    student_id = request.GET.get('student_id')
    if student_id:
        student = get_object_or_404(Student, id=student_id, certificate__Approved=False,)
    else:
        student = pending_students.first()
    # Generate the certificate if it hasn't been generated yet
    # if not student.certificate.certificate_generated:
    #     certificate_image_path = generate_certificate(student)
    #     student.certificate.save()
    # else:
    # certificate_image_path = os.path.join(settings.MEDIA_URL, 'Certificates', f'{student.CBSE_No}_certificate.png')
    certificate_image_path = student.certificate.certificate_path

    # Get the current student's position in the list
    student_ids = list(pending_students.values_list('id', flat=True))
    current_index = student_ids.index(student.id)

    # Determine the next and previous student indices
    next_student = pending_students[current_index + 1] if current_index + 1 < len(student_ids) else None
    prev_student = pending_students[current_index - 1] if current_index - 1 >= 0 else None

    # Render the template with the appropriate context
    context = {
        'student': student,
        'certificate_image_path': certificate_image_path,
        'next_student': next_student,
        'prev_student': prev_student,
    }
    return render(request, "clerk/Preview_Certificates.html", context)

def generate_qr_code(student):
    # The data to encode in the QR code
    # data = "www.google.com"
    data = student.certificate.certificate_id + "," + student.Wing + ", " + student.Location_camp_1 + "," + student.Certificate_type + ", " + str(student.certificate.Date) + ", " +student.School_College_Class
    # Generate the QR code
    qr = pyqrcode.create(data)

    # Path to the 'Qrcode' directory within MEDIA_ROOT
    output_dir = os.path.join(settings.MEDIA_ROOT, 'Qrcode')

    # Create the directory if it does not exist
    os.makedirs(output_dir, exist_ok=True)

    # Define the final path for the QR code image
    qr_image_path = os.path.join(output_dir, f'{student.CBSE_No}_qr.png')

    # Save the image as a PNG file
    qr.png(qr_image_path, scale=6)

    return qr_image_path


def Print_Admit_Cards(request):
    
    return render(request, "clerk/Print_Admit_Cards.html")

def generate_admit_card(student):
    # Load the template image using OpenCV
    template_path = os.path.join(settings.MEDIA_ROOT, 'Template_images', 'admit_card2.png')
    template = cv2.imread(template_path)

    if template is None:
        raise ValueError("Could not load the admit card template image.")

    # Convert the template image from OpenCV format (BGR) to PIL format (RGB)
    template_pil = Image.fromarray(cv2.cvtColor(template, cv2.COLOR_BGR2RGB))

    # Initialize ImageDraw object
    draw = ImageDraw.Draw(template_pil)

    # Load the font from the media folder
    font_path = os.path.join(settings.MEDIA_ROOT, 'Template_images', 'Saans2.ttf')
    font_size = 16
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        raise ValueError("Could not load the specified font.")

    # Define the text and their corresponding positions
    print(model_to_dict(student))
    texts_with_positions = [
        (student.Unit, (242, 246)),
        (student.Admit_Card_No, (920, 230)),
        (student.CBSE_No, (388, 334)),
        (student.Rank, (388, 380)),
        (student.Name, (396, 447)),
        (student.DOB, (260, 500)),
        (student.Fathers_Name, (430, 564)),
        (student.School_College_Class, (488, 616)),
        (student.Year_of_passing_B_Certificate, (488,664)),
        (student.Fresh_Failure, (316,736)),
        (student.Attendance_1st_year, (102,854)),
        (student.Attendance_2nd_year, (322,854)),
        (student.Attendance_3rd_year, (542,854)),
        (student.Name_of_camp_attended_1, (170,976)),
        (student.Date_camp_1, (536,976)),
        (student.Location_camp_1, (828,976)),
        (student.Name_of_camp_attended_2, (170,1000)),
        (student.Date_camp_2, (536,1000)),
        (student.Location_camp_2, (828,1000)),
        (student.Home_Address, (532,1042)),
    ]

    # Add text to the image
    for text, position in texts_with_positions:
        if text:
            draw.text(position, str(text), font=font, fill=(0, 0, 0))

    # If you need to add a photo, paste it on the template
    if student.Photo:
        try:
            insert_image_path = student.Photo.path
            print("image path", insert_image_path)
            insert_image = Image.open(insert_image_path)
            insert_image = insert_image.resize((170, 170))
            image_position = (870, 274)
            template_pil.paste(insert_image, image_position)
        except Exception as e:
            raise ValueError(f"Could not process the student's photo. Error: {e}, Photo Path: {insert_image_path}")

    # Save the final image to a file
    output_dir = os.path.join(settings.MEDIA_ROOT, 'Admit_Cards')
    os.makedirs(output_dir, exist_ok=True)  # Ensure the directory exists
    final_image_path = os.path.join(settings.MEDIA_ROOT, 'Admit_Cards', f'{student.CBSE_No}_admit_card.png')

    try:
        template_pil.save(final_image_path)
        print(f"Admit card saved at: {final_image_path}")  # Debugging
    except Exception as e:
        raise ValueError(f"Could not save the admit card image. Error: {e}")


    return final_image_path

def generate_certificate(student):
    # Define template paths based on the student's Wing and Certificate_Type
    template_filenames = {
        'Army': {'A': 'Army_A.png', 'B': 'Army_B.png', 'C': 'Army_C.png'},
        'Navy': {'A': 'Navy_A.png', 'B': 'Navy_B.png', 'C': 'Navy_C.png'},
        'Air Force': {'A': 'Air_Force_A.png', 'B': 'Air_Force_B.png', 'C': 'Air_Force_C.png'},
    }

    try:
        template_path = os.path.join(settings.MEDIA_ROOT, 'Template_images', template_filenames[student.Wing][student.Certificate_type])
    except KeyError:
        raise ValueError("Invalid Wing or Certificate Type.")

    template = cv2.imread(template_path)
    if template is None:
        raise ValueError("Could not load the certificate template image.")

    # Convert the template image from OpenCV format (BGR) to PIL format (RGB)
    template_pil = Image.fromarray(cv2.cvtColor(template, cv2.COLOR_BGR2RGB))

    # Initialize ImageDraw object
    draw = ImageDraw.Draw(template_pil)

    # Load the font
    font_path = os.path.join(settings.MEDIA_ROOT, 'Template_images', 'Saans2.ttf')
    font_size = 16
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        raise ValueError("Could not load the specified font.")

    # Define text and their corresponding positions based on the certificate type
    if student.Certificate_type == "C":
        texts_with_positions = [
            (student.Unit, (226, 842)),
            (student.CBSE_No, (226, 697)),
            (student.Rank, (748, 697)),
            (student.Name, (226, 764)),
            (student.DOB, (820, 842)),
            (student.Fathers_Name, (829, 764)),
            (student.Certificate_type, (384, 1156)),
            (student.certificate.Place, (217, 1387)),
            (student.certificate.Date, (217, 1477))
        ]
    else:
        texts_with_positions = [
            (student.Unit, (227, 554)),
            (student.CBSE_No, (229, 443)),
            (student.Rank, (660, 443)),
            (student.Name, (244, 500)),
            (student.DOB, (743, 546)),
            (student.Fathers_Name, (741, 500)),
            (student.Certificate_type, (305, 783)),
            (student.certificate.Place, (230, 936)),
            (student.certificate.Date, (227, 991))
        ]

    # Add text to the image
    for text, position in texts_with_positions:
        if text:
            draw.text(position, str(text), font=font, fill=(0, 0, 0))

    # Add the student's photo to the certificate
    if student.Photo:
        try:
            insert_image_path = student.Photo.path
            insert_image = Image.open(insert_image_path)
            insert_image = insert_image.resize((170, 170))
            image_position = (800, 80)
            template_pil.paste(insert_image, image_position)
        except Exception as e:
            raise ValueError(f"Could not process the student's photo. Error: {e}, Photo Path: {insert_image_path}")

    qr_image_path = generate_qr_code(student)
    if qr_image_path:
        try:
            qr_image = Image.open(qr_image_path)
            qr_image = qr_image.resize((170, 170))  # Resize QR code as needed
            qr_position = (80, 80)  # Set QR code position
            template_pil.paste(qr_image, qr_position)
        except Exception as e:
            raise ValueError(f"Could not process the QR code image. Error: {e}, QR Code Path: {qr_image_path}")
        
    # Save the final image
    output_dir = os.path.join(settings.MEDIA_ROOT, 'Certificates')
    os.makedirs(output_dir, exist_ok=True)
    final_image_path = os.path.join(output_dir, f'{student.CBSE_No}_certificate.png')

    try:
        template_pil.save(final_image_path)
        print(f"Certificate saved at: {final_image_path}")
    except Exception as e:
        raise ValueError(f"Could not save the certificate image. Error: {e}")

    return final_image_path
@login_required
def send_for_approval(request, cbse_no):
    student = get_object_or_404(Student, CBSE_No=cbse_no)
    student.rejection_reason = None
    student.admit_card_send_for_approval=True
    student.save()
    return redirect('Preview_Admit_Card')

@login_required
def approve_admit_card(request, cbse_no):
    student = get_object_or_404(Student, CBSE_No=cbse_no)
    student.rejection_reason = None
    student.admit_card_approved = True
    student.save()
    return redirect('Preview_Admit_Card')

@login_required
def reject_admit_card(request, cbse_no):
    if request.method == 'POST':
        student = get_object_or_404(Student, CBSE_No=cbse_no)
        reason = request.POST.get('rejection_reason')
        student.admit_card_approved = False
        student.admit_card_send_for_approval=False
        student.rejection_reason = reason
        student.save()
    return redirect('Preview_Admit_Card')

@login_required
def Register_Students(request):
    if request.user.has_perm('home.can_create_new_candidates'):
        if request.method == 'POST':
            certificate_type=request.POST.get('certificate_type')
            wing=request.POST.get('wing')
            data_file = request.FILES.get('excel_file')
            photos_folder = request.FILES.getlist('photos_folder')
            print(request.user.id)
            if data_file:
                file_extension = os.path.splitext(data_file.name)[1].lower()

                # Read the file based on its extension
                if file_extension in ['.csv']:
                    df = pd.read_csv(data_file)
                elif file_extension in ['.xls', '.xlsx']:
                    df = pd.read_excel(data_file)
                else:
                    return HttpResponseBadRequest("Unsupported file format")

                # Define the column indices corresponding to the model fields
                column_indices = {
                    'CBSE_No': 0, 
                    'Name': 1,     
                    'DOB': 2,      
                    'Fathers_Name': 3,
                    'School_College_Class': 4,
                    'Home_Address': 5,
                    'Admit_Card_No': 6,
                    'Unit': 7,
                    'Rank': 8,
                    'Fresh_Failure': 9,
                    'Year_of_passing_B_Certificate':10,
                    'Attendance_1st_year':11,
                    'Attendance_2nd_year':12,
                    'Attendance_3rd_year':13,
                    'Name_of_camp_attended_1':14,
                    'Date_camp_1':15,
                    'Location_camp_1':16,
                    'Name_of_camp_attended_2':17,
                    'Date_camp_2':18,
                    'Location_camp_2':19
                }

                clerk = Clerk.objects.filter(user=request.user).first()
                # Process each row in the DataFrame
                for _, row in df.iterrows():
                    student_data = {field: row[idx] for field, idx in column_indices.items()}
                    student_data["Certificate_type"]=certificate_type
                    student_data["Wing"]=wing
                    student_data["clerk"] = clerk
                    student_data["colonel"] = clerk.colonel
                    student_data["brigadier"] = clerk.colonel.brigadier
                    student_data["director_general"] = clerk.colonel.brigadier.director_general
                    # Ensure CBSE_No is not missing
                    if pd.isna(student_data['CBSE_No']):
                        return HttpResponseBadRequest("CBSE_No is missing for some records.")

                    # Update or create the student record
                    student, created = Student.objects.update_or_create(
                        CBSE_No=student_data['CBSE_No'],
                        defaults=student_data
                    )

                    # Handle photo upload
                    for photo in photos_folder:
                        if photo.name.startswith(str(student_data['CBSE_No'])):
                            student.Photo.save(photo.name, photo)
                            break

            return redirect('/Register Students/')  # Redirect after processing
        return render(request, "clerk/Register_Students.html")
    else:
        return redirect('/index/')

@login_required
def Rejected_Admit_Cards(request):
    if request.user.has_perm('home.can_view_rejected_applications'):
        # Query to get students with rejected admit cards
        rejected_students = Student.objects.filter(admit_card_approved=False, rejection_reason__isnull=False)
        
        # Pass the data to the template
        context = {
            'rejected_students': rejected_students
        }
        return render(request, "clerk/Rejected_Admit_Cards.html", context)
    else:
        return redirect('/index/')

@login_required
def Student_Details(request):
    view_students = Student.objects.none()  # Default to an empty queryset

    if request.user.groups.filter(name='Clerk').exists():
        clerk_instance = Clerk.objects.get(user=request.user)
        view_students = Student.objects.filter(clerk=clerk_instance)
    elif request.user.groups.filter(name='Colonel').exists():
        colonel_instance = Colonel.objects.get(user=request.user)
        view_students = Student.objects.filter(colonel=colonel_instance)
    elif request.user.groups.filter(name='Brigadier').exists():
        brigadier_instance = Brigadier.objects.get(user=request.user)
        view_students = Student.objects.filter(brigadier=brigadier_instance)
    elif request.user.groups.filter(name='Director_General').exists():
        director_general_instance = Director_General.objects.get(user=request.user)
        view_students = Student.objects.filter(director_general=director_general_instance)

    context = {
        'students': view_students,
        'students_json': json.dumps(list([str(model_to_dict(i)) for i in view_students]), cls=DjangoJSONEncoder)
    }
    return render(request, "clerk/Student_Details.html", context)

@login_required
def All_Students_Previewed(request):
    return render(request,"/All Students Previewed/")

@login_required
def update_student(request):
    if request.method == 'POST':
        student = get_object_or_404(Student, id=request.POST.get("id"))
        # Get data from POST request and handle empty values
        def get_value(field_name, default=None):
            value = request.POST.get(field_name, default)
            if value == '':
                return None
            return value
        
        # Updating fields
        student.Name = get_value('Name')
        student.Fathers_Name = get_value('Fathers_Name')
        student.DOB = get_value('DOB')
        student.Home_Address = get_value('Home_Address')
        student.School_College_Class = get_value('School_College_Class')
        student.Unit = get_value('Unit')
        student.Rank = get_value('Rank')
        student.Year_of_passing_B_Certificate = get_value('Year_of_passing_B_Certificate')
        student.Fresh_Failure = get_value('Fresh_Failure')
        
        # Convert empty strings to None and handle integer conversion
        def parse_int(value):
            try:
                return int(value) if value else None
            except (ValueError, TypeError):
                return None
        
        student.Attendance_1st_year = parse_int(request.POST.get('Attendance_1st_year'))
        student.Attendance_2nd_year = parse_int(request.POST.get('Attendance_2nd_year'))
        student.Attendance_3rd_year = parse_int(request.POST.get('Attendance_3rd_year'))
        
        student.Name_of_camp_attended_1 = get_value('Name_of_camp_attended_1')
        student.Date_camp_1 = get_value('Date_camp_1')
        student.Location_camp_1 = get_value('Location_camp_1')
        
        student.Name_of_camp_attended_2 = get_value('Name_of_camp_attended_2')
        student.Date_camp_2 = get_value('Date_camp_2')
        student.Location_camp_2 = get_value('Location_camp_2')
        student.rejection_reason=None

        # Save the student object
        student.save()
        generate_admit_card(student)

        return redirect('/Student Details')  # Redirect after saving

    return render(request, 'clerk/Student_Details.html', {'student': student})

@login_required
def search_student(request):
    student = None
    context = None
    if 'cbse_no' in request.GET and request.GET.get('cbse_no'):
        cbse_no = request.GET.get('cbse_no')
        student = get_object_or_404(Student, CBSE_No=cbse_no)
        context = {
            'students': [student],
            'students_json': json.dumps([str(model_to_dict(student))], cls=DjangoJSONEncoder)
        }
    return render(request, 'clerk/Student_Details.html', context)
