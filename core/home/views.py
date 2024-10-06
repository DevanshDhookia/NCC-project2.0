from django.shortcuts import render, redirect
from django.http import HttpResponseBadRequest
from django.core.files.base import ContentFile, File
from django.core.files.storage import default_storage
from django.http import HttpResponse,HttpResponseRedirect
import os
import zipfile
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
from common_utils.smtp_manager import SMTPManager
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.views.decorators.cache import cache_control, never_cache
from django.utils.decorators import method_decorator
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.forms.models import model_to_dict
from django.db.models import Q
import pyqrcode 
import png
from datetime import date
from .util import Util
import base64
import pymupdf
import fitz


login_validator = LoginValidator()
jwt_utility = JwtUtility()
utility = Util()
smtp = SMTPManager()

def home(request):
    return redirect("/SignIn/")

def contact(request):
    return render(request, "Login_Page/contact.html")

def custom_404_view(request):
    return render(request, '404.html', status=404)

def SignIn(request):
    if request.user.is_authenticated:  # If the user is already authenticated, avoid signing in again
        return redirect("/admin/" if request.user.is_superuser else "/user/")  # Admin panel for admin user, else user panel

    if request.method == 'POST':
        try:
            data = request.POST
            user = authenticate(username=data.get("username"), password=data.get("password"))
            if user is not None:
                login(request, user)
                token = jwt_utility.get_jwt_token({"username": user.username})
                request.session["token"] = token
                return redirect("/admin/" if user.is_superuser else "/user/")
            else:
                messages.error(request, "Invalid login credentials")
                return redirect("/SignIn/")
        except Exception as e:
            print(f"An error occurred: {e}")
            messages.error(request, "Some error occurred. Please try again.")
    
    return render(request, "Login_Page/SignIn.html", {"page_name": "Ludiflex | Login & Registration"})

    
def forgot_password(request):
    if request.user.is_authenticated:
        return redirect("/change-password/")
    else:
        context = {"page_name": "Ludiflex | Login & Registration", "otp": False}
        if request.method == "POST":
            user_name = request.POST.get("username")
            otp = request.POST.get("otp")
            isotpcall = request.POST.get("isotp")
            try:
                user = User.objects.get(username=user_name)
                context["username"] = user_name
                if not otp and isotpcall == 'True':
                    context["otp"] = True
                    messages.error(request, "OTP is required")
                elif not otp:
                    if user is not None:
                        email = user.email
                        if not email:
                            messages.error(request,"Email address not found for the user")
                        else:
                            data = utility.generate_and_save_otp(user_name)
                            if(data[0]):
                                try:
                                    smtp.send_email(user_name, email, data[1])
                                    messages.info(request, "OTP Generated. Valid for 10 minutes.")
                                    context["otp"] = True
                                except Exception as e:
                                    print("Exception occured while sending email", e)
                                    messages.error(request, "Unable to send email")
                            else:
                                messages.error(request, "Unable to generate OTP. Please try later.")
                    else:
                        messages.error(reqest, "User details not found")
                else:
                    otp_validation_result = utility.validate_otp(user_name, otp)
                    if otp_validation_result[0]:
                        password1 = request.POST.get("new-pass")
                        password2 = request.POST.get("new-pass-1")
                        if not password1 or not password2:
                            context["otp"] = False
                            messages.error(request, "All fields are required, Please regerate the OTP")
                        else:
                            if password1 != password2:
                                context["otp"] = True
                                messages.error(request, "Passwords does not match")
                            else:
                                user.set_password(password1)
                                user.save()
                                messages.info(request, "Password updated successfully, Please login")
                    else:
                        context["username"]=user_name
                        context["otp"] = True
                        messages.error(request, otp_validation_result[1])
                                            
            except Exception as e:
                print("User not found", e)
                messages.info(request, "User not found")
        return render(request, "Login_Page/reset_password.html", context=context)

@login_required
def change_password(request):
    if request.method == 'POST':
        old_password = request.POST.get("old-pass")
        new_pass = request.POST.get("new-pass")
        new_pass_c = request.POST.get("new-pass-1")
        if request.user.check_password(old_password):
            if new_pass == old_password:
                messages.info(request, "New password cannot be same as old password")
            else:
                if new_pass == new_pass_c:
                    user = User.objects.get(id = request.user.id)
                    user.set_password(new_pass)
                    user.save()
                    messages.info(request, "Password updated successfully")
                    return redirect("/user/")
                else:
                    messages.error(request, "New password and confirm pasword does not match.")
        else:
            messages.error(request, "Incorrect old password.")
    return render(request, "Login_Page/reset_password.html", {"page_name": "NCC (National Cadet Corps)"})


@login_required
def generate_otp(request):
    if request.user.has_perm('home.can_create_new_users'):
        if request.method == 'POST':
            username = request.POST.get('otp-username')
            typee = request.POST.get("type")
            otpp = request.POST.get("otp")

@login_required
def register(request):
    if request.user.has_perm('home.can_create_new_users'):
        if request.method == 'POST':
            username = request.POST.get('username')
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            firstname = request.POST.get('firstName')
            lastname = request.POST.get('lastName')
            email = request.POST.get('email')
            otp = request.POST.get("otp")
            # Basic validation
            if not username or not email:
                messages.error(request, "Username and Email required to generate OTP.")
                return redirect('/register/')
            if(not otp and not password1 and not password2):
                data = utility.generate_and_save_otp(username)
                if(data[0]):
                    try:
                        smtp.send_email(username, email, data[1])
                        messages.error(request, "OTP Generated. Valid for 10 minutes.")
                    except Exception as e:
                        print("Exception occured while sending email", e)
                        message.error(request, "Unable to send email")
                else:
                    messages.error(request, "Unable to generate OTP. Please try later.")
                context={
                    "firstName": firstname,
                    "lastName": lastname,
                    "email": email,
                    "username": username,
                    "otpEnabled": True
                }
                return render(request, 'Login_Page/register.html', context)
            if not username or not password1 or not password2:
                context={
                    "firstName": firstname,
                    "lastName": lastname,
                    "email": email,
                    "username": username,
                    "otpEnabled": True
                }
                context={"otpEnabled": False}
                messages.error(request, "All fields are required.")
                return render(request, 'Login_Page/register.html', context)
            if not otp:
                context={
                    "firstName": firstname,
                    "lastName": lastname,
                    "email": email,
                    "username": username,
                    "otpEnabled": True
                }
                context={"otpEnabled": False}
                messages.error(request, "OTP is required.")
                return render(request, 'Login_Page/register.html', context)
            if password1 != password2:
                context={
                    "firstName": firstname,
                    "lastName": lastname,
                    "email": email,
                    "username": username,
                    "otpEnabled": True
                }
                context={"otpEnabled": False}
                messages.error(request, "Passwords do not match.")
                return render(request, 'Login_Page/register.html', context)

            if User.objects.filter(username=username).exists():
                context={"otpEnabled": False}
                messages.error(request, "Username already exists.")
                return render(request, 'Login_Page/register.html', context)

            otp_validation_result = utility.validate_otp(username, otp)
            if otp_validation_result[0]:
                # Create new user
                user = User.objects.create_user(username=username)
                user.first_name=firstname
                user.last_name=lastname
                user.email = email
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
            else:
                context={
                    "firstName": firstname,
                    "lastName": lastname,
                    "email": email,
                    "username": username,
                    "otpEnabled": True
                }
                messages.error(request, otp_validation_result[1])
                return render(request, 'Login_Page/register.html', context)
                
        context = {"otpEnabled": False}
        return render(request, 'Login_Page/register.html', context)
    else:
        return redirect("/index/")

def user_logout(request):
    request.session.delete("token")
    request.session.flush()
    logout(request)
    return redirect("/SignIn/")

#-------------- Home Page Views -------------#
def index(request):
    if request.user.is_authenticated:
        return redirect("/user/")
    else:
        return redirect("/SignIn/")

@login_required
def clerk_page(request, user_id='default'):
    try:
        if login_validator.is_user_logged_in(request) and request.user.is_authenticated:
            # user_id = request.GET.get("user_id")
            admitcard_generated_students = 0
            send_for_approval_students = 0
            reject_admit_card_students = 0
            admitcard_approved = 0
            army_students = 0
            navy_students = 0
            af_students = 0
            a_cert_generated = 0
            b_cert_generated = 0
            c_cert_generated = 0
            a_cert_pending_approval = 0
            b_cert_pending_approval = 0
            c_cert_pending_approval = 0
            total_certificates = 0
            total_cert_approved = 0
            total_cert_pending_approval = 0
            total_rejected_certs = 0
            groupp = None
            
            juniors = None
            students_list = None
            if request.user.groups.filter(name='Director_General').exists():
                groupp = "dg"
                juniors = Brigadier.objects.filter(director_general_id = Director_General.objects.get(user_id=request.user.id).id)
                if user_id != 'default':
                    try:
                        if Brigadier.objects.get(user_id = user_id).director_general_id == Director_General.objects.get(user_id = request.user.id).id:
                            students_list = Student.objects.filter(brigadier_id = Brigadier.objects.get(user_id=user_id), director_general_id = Director_General.objects.get(user_id=request.user.id).id)
                        else:
                            raise Exception("You are not entitled to view this user")
                    except Exception as e:
                        print(e)
                        messages.info(request, "You are not entitled to view this user details")
                        return redirect("/user/")
                else:
                    students_list = Student.objects.filter(director_general_id = Director_General.objects.get(user_id=request.user.id).id)
            
            if request.user.groups.filter(name='Brigadier').exists():
                groupp = "bg"
                juniors = Colonel.objects.filter(brigadier_id = Brigadier.objects.get(user_id=request.user.id).id)
                if user_id != 'default':
                    try:
                        if Colonel.objects.get(user_id = user_id).brigadier_id == Brigadier.objects.get(user_id = request.user.id).id:
                            students_list = Student.objects.filter(colonel_id = Colonel.objects.get(user_id=user_id).id, brigadier_id = Brigadier.objects.get(user_id=request.user.id).id)
                        else:
                            raise Exception("You are not entitled to view this user")
                    except Exception as e:
                        print(e)
                        messages.info(request, "You are not entitled to view this user details")
                        return redirect("/user/")
                else:
                    students_list = Student.objects.filter(brigadier_id = Brigadier.objects.get(user_id=request.user.id).id)

            if request.user.groups.filter(name='Colonel').exists():
                groupp = "co"
                juniors = Clerk.objects.filter(colonel_id = Colonel.objects.get(user_id=request.user.id).id)
                if user_id != 'default':
                    try:
                        if Clerk.objects.get(user_id = user_id).colonel_id == Colonel.objects.get(user_id = request.user.id).id:
                            students_list = Student.objects.filter(clerk_id = Clerk.objects.get(user_id=user_id), colonel_id = Colonel.objects.get(user_id=request.user.id).id)
                        else:
                            raise Exception("You are not entitled to view this user")
                    except Exception as e:
                        print(e)
                        messages.info(request, "You are not entitled to view this user details")
                        return redirect("/user/")
                else:
                    students_list = Student.objects.filter(colonel_id = Colonel.objects.get(user_id=request.user.id).id)
            if request.user.groups.filter(name='Clerk').exists():
                groupp = "cl"
                juniors = None
                students_list = Student.objects.filter(clerk_id = Clerk.objects.get(user_id=request.user.id).id)
            if juniors is not None :
                juniors = [User.objects.get(id = junior.user_id) for junior in juniors]
            for student in students_list:
                if student.admit_card_approved:
                    admitcard_approved += 1
                if student.admit_card_generated:
                    admitcard_generated_students += 1
                if student.admit_card_send_for_approval and not student.admit_card_approved:
                    send_for_approval_students += 1
                if student.rejection_reason:  # This checks if rejection_reason is not None and not an empty string
                    reject_admit_card_students += 1
                if student.Wing == 'Army':
                    army_students += 1
                if student.Wing == 'Navy':
                    navy_students += 1
                if student.Wing == 'Air Force':
                    af_students += 1
                if student.Certificate_type == 'A' and student.certificate and student.certificate.Approved == True:
                    total_certificates += 1
                    a_cert_generated += 1
                    total_cert_approved += 1
                if student.Certificate_type == 'B' and student.certificate and  student.certificate.Approved == True:
                    total_certificates += 1
                    b_cert_generated += 1
                    total_cert_approved += 1
                if student.Certificate_type == 'C' and student.certificate and  student.certificate.Approved == True:
                    total_certificates += 1
                    c_cert_generated += 1
                    total_cert_approved += 1
                if student.Certificate_type == 'A' and student.certificate and  student.certificate.Approved == False:
                    total_certificates += 1
                    a_cert_pending_approval += 1
                    total_cert_pending_approval += 1
                if student.Certificate_type == 'B' and student.certificate and  student.certificate.Approved == False:
                    total_certificates += 1
                    b_cert_pending_approval += 1
                    total_cert_pending_approval += 1
                if student.Certificate_type == 'C' and student.certificate and  student.certificate.Approved == False:
                    total_certificates += 1
                    c_cert_pending_approval += 1
                    total_cert_pending_approval += 1
                if student.certificate and  student.certificate.Approved == False and student.certificate.Rejected_by is not None:
                    total_rejected_certs += 1
                    
            context = {
                'total_students': students_list,
                'admitcard_generated_students': admitcard_generated_students,
                'send_for_approval_students': send_for_approval_students,
                'reject_admit_card_students': reject_admit_card_students,
                "admit_card_approved": admitcard_approved,
                "juniors": juniors,
                "army_students": army_students,
                "navy_students": navy_students,
                "air_force_students": af_students,
                "a_cert_generated": a_cert_generated,
                "b_cert_generated": b_cert_generated,
                "c_cert_generated": c_cert_generated,
                "a_cert_pending_approval": a_cert_pending_approval,
                "b_cert_pending_approval": b_cert_pending_approval,
                "c_cert_pending_approval": c_cert_pending_approval,
                "total_certificates": total_certificates,
                "total_cert_approved": total_cert_approved,
                "total_cert_pending_approval": total_cert_pending_approval,
                "total_rejected_certs": total_rejected_certs,
                "groupp": groupp
            }


            return render(request, "clerk/clerk.html", context)
        else:
           return redirect("/SignIn/")
    except Exception as e:
        messages.error(request, "Some error occurred")
        print("Exception occurred: ", e)
        return redirect("/index/")
@login_required
def Add_Result(request):
    return render(request, "clerk/Add_Result.html")

@login_required
def add_result_data(request):
    try:
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
                print("Starting to prcess the result upload file")
                # try:
                excel_file = request.FILES.get("excel_file")
                if excel_file:
                    file_extension = os.path.splitext(excel_file.name)[1]
                    df = None
                    if file_extension in ['.csv']:
                        df = pd.read_csv(excel_file)
                    elif file_extension in ['.xls', '.xlsx']:
                        df = pd.read_excel(excel_file)
                    else:
                        messages.info(request, "The uploaded file format is not supproted")
                        return redirect("/Add Result/")
                    print("Excel file read complete")
                    column_indices = {
                        'CBSE_No': 1,
                        'Parade_attendance': 9,
                        'Paper1_W': 11,
                        'Paper1_P': 12,
                        'Paper1_T': 13,
                        'Paper2_W': 14,
                        'Paper2_P': 15,
                        'Paper2_T': 16,
                        'Paper3_W': 17,
                        'Paper4_W': 18,
                        'Paper4_P': 19,
                        'Paper4_T': 20,
                        'Bonus_marks': 22,
                        'Final_total': 23,
                        'Grade': 24
                    }
                    print("Start of file parsing")
                    col_count = 0
                    for _, row in df.iterrows():
                        if col_count > 13:
                            result_data = {field: row[idx] for field, idx in column_indices.items()}
                            pass_paper_1 = ((float(result_data['Paper1_T']) / 80) * 100) >= 33
                            pass_paper_2 = ((float(result_data['Paper2_T']) / 60) * 100) >= 33
                            pass_paper_3 = ((float(result_data['Paper3_W']) / 210) * 100) >= 33
                            pass_paper_4 = ((float(result_data['Paper4_T']) / 150) * 100) >= 33
                            percentage_obt = ((float(result_data['Final_total']) / 500) * 100)
                            result_data["Grade"] = "A" if percentage_obt >= 70 else "B" if percentage_obt >= 55 else "C" if percentage_obt >= 33 else "F"
                            if pass_paper_1 and pass_paper_2 and pass_paper_3 and pass_paper_4 and percentage_obt >= 33:
                                result_data["Pass"] = True
                            else:
                                result_data["Pass"] = False
                            cbse_no = result_data["CBSE_No"]
                            result_data.pop("CBSE_No")
                            student = Student.objects.filter(CBSE_No = cbse_no).first()
                            if student:
                                if np.isnan(result_data["Parade_attendance"]):
                                    result_data["Parade_attendance"] = 0
                                if np.isnan(result_data['Paper1_W']):
                                    result_data["Paper1_W"] = 0
                                if np.isnan(result_data['Paper1_P']):
                                    result_data["Paper1_P"] = 0
                                if np.isnan(result_data['Paper1_T']):
                                    result_data["Paper1_T"] = 0
                                if np.isnan(result_data['Paper2_W']):
                                    result_data["Paper2_W"] = 0
                                if np.isnan(result_data['Paper2_P']):
                                    result_data["Paper2_P"] = 0
                                if np.isnan(result_data['Paper2_T']):
                                    result_data["Paper2_T"] = 0
                                if np.isnan(result_data['Paper3_W']):
                                    result_data["Paper3_W"] = 0
                                if np.isnan(result_data['Paper4_W']):
                                    result_data["Paper4_W"] = 0
                                if np.isnan(result_data['Paper4_P']):
                                    result_data["Paper4_P"] = 0
                                if np.isnan(result_data['Paper4_T']):
                                    result_data["Paper4_T"] = 0
                                if np.isnan(result_data['Bonus_marks']):
                                    result_data["Bonus_marks"] = 0
                                if np.isnan(result_data['Final_total']):
                                    result_data["Final_total"] = 0

                                result = Result.objects.create(
                                    **result_data
                                )
                                student.result = result
                                student.save()
                            else:
                                print("Student record not available for cbse no: ", cbse_no)
                        
                        col_count += 1
                    print("End of file parsing")
                    messages.info(request, "Student results added successfully")
                    return redirect("/Add Result/")
                else:
                    messages.info(request, "Not able to read the uploaded file")
                    return redirect("/Add Result/")
                # except Exception as e:
                #     print(e)
                #     messages.info(request, "Unable to process record")
                #     return redirect("/Add Result/")
                        

                        

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
    except Exception as e:
        print("Exception occurred: ", e)
        messages.error(request, "Some error occurred")
        return redirect("/index/")

@login_required
def results(request, page):
    try:
        if request.user.has_perm("home.view_result"):
            current_page = int(page)
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
            
            total_pages = len(results_data) // 10 if len(results_data) % 10 == 0 else (len(results_data) // 10) + 1
            if total_pages == 0:
                total_pages = 1
            if current_page == 0:
                current_page = 1
            elif current_page > total_pages:
                current_page = total_pages
            offset = ((current_page-1) * 10)
            last_record_index = (current_page * 10)
            if last_record_index > len(results_data):
                last_record_index = len(results_data)
            
            results_data = results_data[offset: last_record_index]
            
            bonus_marks_cat = BonusMarksCategories.objects.all()
            bonus_marks_ser = json.dumps([model_to_dict(item) for item in bonus_marks_cat], cls=DjangoJSONEncoder)
            return_data = [{"id": student.id,"student_id": student.CBSE_No, "result": model_to_dict(student.result), "student_name": student.Name, "college": student.School_College_Class, "unit": student.Unit,"rank": student.Rank, "p_1_total": student.result.Paper1_T, "p_2_total": student.result.Paper2_T, "p_3_total": student.result.Paper3_W, "p_4_total": student.result.Paper4_T, "cert_generated": student.certificate_id != None} for student in results_data]
            serialized_return_data = json.dumps(list(return_data), cls=DjangoJSONEncoder)
            return render(request, "clerk/view_results.html", {"result_data": return_data, "serialized_result_data": serialized_return_data, "bonus_marks_ser": bonus_marks_ser, "bonus_marks": bonus_marks_cat, 'current_page': current_page, 'total_pages': total_pages, 'disable_prev': current_page == 1, 'disable_next': current_page >= total_pages, 'prev_page': current_page - 1, 'next_page': current_page + 1, 'page_range': range(1, total_pages+1)})
        else:
            return redirect('/index/')
    except Exception as e:
        print("Some exception occurred", e)
        messages.error(request, "Some error occurred")
        return redirect('/index/')


@login_required
def Preview_Admit_Card(request, page):
    try:
        if login_validator.is_user_logged_in(request) and request.user.is_authenticated:
            current_page = int(page)
        
            # Retrieve all pending students ordered by ID
            pending_students = []
            if request.user.groups.filter(name='Colonel').exists():
                pending_students = Student.objects.filter(admit_card_approved=False, rejection_reason=None, admit_card_send_for_approval=True, colonel_id=Colonel.objects.filter(user_id=request.user.id)[0].id).order_by('id')
            elif request.user.groups.filter(name='Clerk').exists():
                pending_students = Student.objects.filter(admit_card_approved=False, rejection_reason=None, admit_card_send_for_approval=False, clerk_id=Clerk.objects.filter(user_id=request.user.id)[0].id).order_by('id')
                # pending_students = Student.objects.filter(clerk_id=Clerk.objects.filter(user_id=request.user.id)[0].id).order_by('id')
            else:
                messages.error(request, "You do not have permission to perform this action.")
                return redirect('/user/')
            if not pending_students.exists():
                # If no students are left to preview, render the "All Students Previewed" page
                return render(request, "clerk/All_Students_Previewed.html")
            total_pages = len(pending_students) // 10 if len(pending_students) % 10 == 0 else (len(pending_students) // 10) + 1
            if total_pages == 0:
                total_pages = 1
            if current_page == 0:
                current_page = 1
            elif current_page > total_pages:
                current_page = total_pages
            offset = ((current_page-1) * 10)
            last_record_index = (current_page * 10)
            if last_record_index > len(pending_students):
                last_record_index = len(pending_students)
            
            curr_pending_students = pending_students[offset: last_record_index]
            pending_students = [str(model_to_dict(student)) for student in pending_students]
            # Get the current student ID from the request or default to the first pending student
            context = {
                "all_students": json.dumps(pending_students, cls=DjangoJSONEncoder),   
                'pending_students': curr_pending_students,
                'current_page': current_page,
                'total_pages': total_pages,
                'disable_prev': current_page == 1,
                'disable_next': current_page >= total_pages,
                'prev_page': current_page - 1,
                'next_page': current_page + 1,
                'page_range': range(1, total_pages+1)
            }
            return render(request, "clerk/Preview_Admit_Card.html", context)
        else:
            return redirect("/SignIn/")
    except Exception as e:
        print("Some exception occurred", e)
        messages.error(request, "Some error occurred")
        return redirect("/index/")
    
@login_required
def bulk_generate_certs(request):
    cbse_no_list = request.POST.getlist("checkedBoxes[]")
    page = request.POST.get("page")
    try:
        for cbse_no in cbse_no_list:
            student = Student.objects.filter(CBSE_No = cbse_no)
            if student.exists():
                student = student[0]
                id = str(student.id)
                year = str(date.today().year)
                try:
                    cert = None
                    certificate_id = cbse_no[0:2]+"/"+student.Certificate_type + " Cert/"+student.Unit+"/"+year+ "/" + str(student.clerk.certificate_no_current)
                    certificate = Certificate.objects.filter(certificate_id=certificate_id)
                    if certificate.exists():
                        cert = certificate[0]
                        cert.certificate_generated = True
                        cert.Date = date.today()
                        cert.Approval_stage='0'
                        cert.Generation_date = date.today()
                        cert.Place = "Kanpur"
                        cert.Rejected_by=None
                        cert.Rejected_reason=None
                        cert.save()
                    else:
                        cert = Certificate.objects.create(
                            certificate_id = cbse_no[0:2]+"/"+student.Certificate_type + " Cert/"+student.Unit+"/"+year+ "/" + str(student.clerk.certificate_no_current),
                            certificate_generated = True,
                            Date = date.today(),
                            Approval_stage='0',
                            Generation_date = date.today(),
                            Place = "Kanpur"
                        )
                        student.clerk.certificate_no_current+=1
                        student.clerk.save()
                except Exception as error:
                    print(error)
                    messages.error(request, "Certificate already generated for the student")
                student.certificate = cert
                student.save()
                try:
                    certificate_image_path = generate_certificate(student)
                    cert.certificate_path = certificate_image_path
                    cert.save()
                    student.certificate = cert
                    student.save()
                except Exception as e:
                    print("Unable to generate certificate", e)
                    student.certificate = None
                    student.save()
                    cert.delete()
                    messages.info(request, "Error while generating certificate")
        messages.info(request, "Certificate Sent for Approval")
    except Exception as e:
        print("Exception occurred while generating certificate", e)
        messages.error(request, "Error occurred")
    return HttpResponse({"status": 200, "message": "success"}, content_type='application/json', status=200)

@login_required
def generate_certificate_action(request, cbse_no, page):
    student = Student.objects.filter(CBSE_No = cbse_no)
    print('Generating certificate for student with CBSE No: ', cbse_no)
    if student.exists():
        student = student[0]
        id = str(student.id)
        year = str(date.today().year)
        try:
            if(student.clerk.certificate_no_current>student.clerk.certificate_no_end):
                messages.error(request, "Certificate range is exhausted.")
                return redirect("/view-results/"+str(page)+"/")
            cert = None
            certificate_id = cbse_no[0:2]+"/"+student.Certificate_type + " Cert/"+student.Unit+"/"+year+ "/" + str(student.clerk.certificate_no_current)
            certificate = Certificate.objects.filter(certificate_id=certificate_id)
            if certificate.exists():
                print("Existing certificate found for student")
                cert = certificate[0]
                cert.certificate_generated = True
                cert.Date = date.today().strftime("%d %m %Y")
                cert.Approval_stage='0'
                cert.Generation_date = date.today()
                cert.Place = "Kanpur"
                cert.Rejected_by=None
                cert.Rejected_reason=None
                cert.save()
            else:
                cert = Certificate.objects.create(
                    certificate_id = cbse_no[0:2]+"/"+student.Certificate_type + " Cert/"+student.Unit+"/"+year+ "/" + str(student.clerk.certificate_no_current),
                    certificate_generated = True,
                    Date = date.today(),
                    Approval_stage='0',
                    Generation_date = date.today(),
                    Place = "Kanpur"
                    )
                student.clerk.certificate_no_current+=1
                student.clerk.save()
        except Exception as error:
            print(error)
            messages.error(request, "Certificate already generated for the student")
            return redirect("/view-results/"+str(page)+"/")
        student.certificate = cert
        student.save()
        try:
            certificate_image_path = generate_certificate(student)
            cert.certificate_path = certificate_image_path
            cert.save()
            student.certificate = cert
            student.save()
        except Exception as e:
            print("Unable to generate certificate", e)
            student.certificate = None
            student.save()
            cert.delete()
            messages.info(request, "Error while generating certificate")
            return redirect("/view-results/"+str(page)+"/")
        messages.info(request, "Certificate generated")
    else:
        messages.error(request, "Student not found with provided CBSE No.")
    return redirect("/view-results/"+str(page)+"/")

@login_required
@never_cache
def Preview_Certificates(request, page):
    try:
        current_page = int(page)
        # Determine the user's role and fetch pending students accordingly
        pending_students=[]
        if request.user.groups.filter(name='Director_General').exists():
            director_general_id = Director_General.objects.get(user_id=request.user.id).id
            pending_students = Student.objects.filter(
                certificate__Approval_stage=3,
                certificate__Rejected_reason=None,
                director_general_id=director_general_id,
                certificate__certificate_generated=True
            ).order_by('id')

        elif request.user.groups.filter(name='Brigadier').exists():
            brigadier_id = Brigadier.objects.get(user_id=request.user.id).id
            pending_students = Student.objects.filter(
                certificate__Approved=False,
                certificate__Approval_stage=2,
                certificate__Rejected_reason=None,
                brigadier_id=brigadier_id,
                certificate__certificate_generated=True
            ).order_by('id')

        elif request.user.groups.filter(name='Colonel').exists():
            colonel_id = Colonel.objects.get(user_id=request.user.id).id
            pending_students = Student.objects.filter(
                certificate__Approved=False,
                certificate__Approval_stage=1,
                certificate__Rejected_reason=None,
                colonel_id=colonel_id,
                certificate__certificate_generated=True
            ).order_by('id')
        elif request.user.groups.filter(name='Clerk').exists():
            clerk_id = Clerk.objects.get(user_id=request.user.id).id
            pending_students = Student.objects.filter(
                certificate__Approved=False,
                certificate__Approval_stage=0,
                certificate__Rejected_reason=None,
                clerk_id=clerk_id,
                certificate__certificate_generated=True
            ).order_by('id')
        else:
            messages.error(request, "You do not have permission to perform this action.")
            return redirect('/user/')

        if not pending_students.exists():
            return render(request, "clerk/All_Students_Previewed.html")
        total_pages = len(pending_students) // 10 if len(pending_students) % 10 == 0 else (len(pending_students) // 10) + 1
        if total_pages == 0:
            total_pages = 1
        if current_page == 0:
            current_page = 1
        elif current_page > total_pages:
            current_page = total_pages
        offset = ((current_page-1) * 10)
        last_record_index = (current_page * 10)
        if last_record_index > len(pending_students):
            last_record_index = len(pending_students)
            
        curr_pending_students = pending_students[offset: last_record_index]
        pending_students = [str(model_to_dict(student)) for student in pending_students]
        # Get the current student from request or default to the first in the list 
        
        context = {
            'pending_students': curr_pending_students,
            'all_students': json.dumps(pending_students, cls=DjangoJSONEncoder),
            'current_page': current_page,
            'total_pages': total_pages,
            'disable_prev': current_page == 1,
            'disable_next': current_page >= total_pages,
            'prev_page': current_page - 1,
            'next_page': current_page + 1,
            'page_range': range(1, total_pages+1)
        }
        return render(request, "clerk/Preview_Certificates.html", context)
    except Exception as e:
        print("Some exception occurred: ", e)
        messages.error(request, 'Some error occurred')
        return redirect("/index/")

@login_required
def print_certificate(request):
    folder_path = os.path.join(settings.MEDIA_ROOT, 'Certificates')
    try:
        if request.method == 'POST' and 'download' in request.POST:
            zip_file_name = 'certificates.zip'
            zip_file_path = os.path.join(settings.MEDIA_ROOT, zip_file_name)
            with zipfile.ZipFile(zip_file_path, 'w') as zipf:
                for root, dirs, files in os.walk(folder_path):
                    for file in files:
                        if "back" in file or ".pdf" in file:
                            print(file)
                            print("skipping file ", file)
                            pass
                        else:
                            cbse_no = "_".join(file.split("_")[0:-1])
                            
                            if check_generated_by_cbse_no(cbse_no, 'c', request.user)[0]:
                                print("processing for ", file)
                                file_path = os.path.join(root, file)
                                file_back_path = os.path.join(root, cbse_no+"_back_certificate.png")
                                pdf_path = os.path.join(root, cbse_no+"_certificate.pdf")
                                doc = fitz.open()
                        
                                page = doc.new_page()
                                image_rectangle = fitz.Rect(0, 0, 600, 850)
                                page.insert_image(image_rectangle, stream=open(file_path, "rb").read(), xref=0)
                                page2 = doc.new_page()
                                page2.insert_image(image_rectangle, stream=open(file_back_path, "rb").read(), xref=0)
                                doc.save(pdf_path)
                                
                                zipf.write(pdf_path, os.path.relpath(pdf_path, folder_path))
                                os.remove(pdf_path)
            # Serve the zip file as a downloadable response
            with open(zip_file_path, 'rb') as zipf:
                response = HttpResponse(zipf.read(), content_type='application/zip')
                response['Content-Disposition'] = f'attachment; filename={zip_file_name}'
            
            # Close the response before deleting the file
            response.close()

            # Delete the ZIP file from the server after the download
            os.remove(zip_file_path)

            # Set a success message
            messages.success(request, 'The Certificates folder has been successfully downloaded.')

            # Redirect back to the same page after download
            return response
        if request.method == 'POST' and 'single' in request.POST:
            cbse_no = request.POST.get("cbse_no")
            st_check_result = check_generated_by_cbse_no(cbse_no, 'c', request.user)
            if st_check_result[0]:
                file_path = os.path.join(folder_path, cbse_no + "_certificate.png")
                file_back_path = os.path.join(folder_path, cbse_no + "_back_certificate.png")
                pdf_path = os.path.join(folder_path, cbse_no+"_certificate.pdf")
                if os.path.exists(file_path):
                    doc = fitz.open()
                    
                    page = doc.new_page()
                    image_rectangle = fitz.Rect(0, 0, 600, 850)
                    page.insert_image(image_rectangle, stream=open(file_path, "rb").read(), xref=0)
                    page2 = doc.new_page()
                    page2.insert_image(image_rectangle, stream=open(file_back_path, "rb").read(), xref=0)
                    doc.save(pdf_path)
                    
                    
                    with open(pdf_path, "rb") as certificate:
                        response = HttpResponse(certificate.read(), content_type="application/pdf")
                        response['Content-Disposition'] = f'attachment; filename={cbse_no}_certificate.pdf'
                    response.close()
                    os.remove(pdf_path)
                    return response
                else:
                    messages.error(request, "Certificate not available for this CBSE No.")
            else:
                messages.error(request, st_check_result[1])
        if request.method == 'POST' and 'duplicate' in request.POST:
            cbse_no = request.POST.get("cbse_no")
            st_check_result = check_generated_by_cbse_no(cbse_no, 'c', request.user)
            if st_check_result[0]:
                new_file_name=cbse_no+"_dup_certificate.png"
                file_path = os.path.join(folder_path, cbse_no + "_certificate.png")
                duplicate_file_path = os.path.join(folder_path, new_file_name)
                if os.path.exists(file_path):
                    
                    certificate_image = cv2.imread(file_path)
                    template_pil = Image.fromarray(cv2.cvtColor(certificate_image, cv2.COLOR_BGR2RGB))
                    draw = ImageDraw.Draw(template_pil)
                    # Load the font
                    font_path = os.path.join(settings.MEDIA_ROOT, 'Template_images', 'Saans2.ttf')
                    font_size = 20
                    try:
                        font = ImageFont.truetype(font_path, font_size)
                    except IOError:
                        raise ValueError("Could not load the specified font.")

                    draw.text((850, 20), "DUPLICATE", font=font, fill=(255,255,255))
                    template_pil.save(duplicate_file_path)
                    with open(duplicate_file_path, "rb") as certificate:
                        response = HttpResponse(certificate.read(), content_type="image/png")
                        response['Content-Disposition'] = f'attachment; filename={new_file_name}'
                    response.close()
                    os.remove(duplicate_file_path)
                    return response
                else:
                    messages.error(request, "Certificate not available for this CBSE No.")
            else:
                messages.error(request, st_check_result[1])
    except Exception as e:
        messages.error(request, "Not able to download the certificates, Please try later")
        # Render the template for GET requests
    return render(request, "clerk/print_certificate.html")

def check_generated_by_cbse_no(cbse_no, rtype, user):
    student_data = None
    if user.groups.filter(name='Director_General').exists():
        director_general_id = Director_General.objects.get(user_id=user.id).id
        student_data = Student.objects.filter(
           director_general_id=director_general_id,
           CBSE_No = cbse_no
        ).order_by('id')

    elif user.groups.filter(name='Brigadier').exists():
        brigadier_id = Brigadier.objects.get(user_id=user.id).id
        student_data = Student.objects.filter(
           brigadier_id=brigadier_id,
           CBSE_No = cbse_no
       ).order_by('id')

    elif user.groups.filter(name='Colonel').exists():
       colonel_id = Colonel.objects.get(user_id=user.id).id
       student_data = Student.objects.filter(
           colonel_id=colonel_id,
           CBSE_No = cbse_no
       ).order_by('id')
    elif user.groups.filter(name='Clerk').exists():
       clerk_id = Clerk.objects.get(user_id=user.id).id
       student_data = Student.objects.filter(
           clerk_id=clerk_id,
           CBSE_No = cbse_no
       ).order_by('id')
    else:
        messages.error(request, "You do not have permission to perform this action.")
        return redirect('/user/')
    if student_data:
        if rtype == 'c':
            if student_data[0].certificate:
                if student_data[0].certificate.Approved==True:
                    return True, ""
                else:
                    return False, "Certificate is not approved for the student"
            else:
                return False, "Certificate not available for this student"
        if rtype == 'a':
            if student_data[0].admit_card_generated:
                if student_data[0].admit_card_approved==True:
                    return True, ""
                else:
                    return False, "Admit Card is not approved for the student"
            else:
                return False, "Admit Card not available for this student"
    else:
        return False, "Student details does not exist"

def generate_qr_code(student):
    # The data to encode in the QR code
    # data = "www.google.com"
    data = student.CBSE_No + "," + student.Name + "," + student.Fathers_Name + ", " + student.Unit + "," + student.School_College_Class + ", " + str(student.Year) + ", " + student.result.Grade + "," + "Certified By ACG Software"
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
    folder_path = os.path.join(settings.MEDIA_ROOT, 'Admit_Cards')
    if request.method == 'POST' and 'download' in request.POST:
        zip_file_name = 'Admit_Cards.zip'
        zip_file_path = os.path.join(settings.MEDIA_ROOT, zip_file_name)
        with zipfile.ZipFile(zip_file_path, 'w') as zipf:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    cbse_no = "_".join(file.split("_")[0:-2])
                    if check_generated_by_cbse_no(cbse_no, 'a', request.user)[0]:
                        file_path = os.path.join(root, file)
                        zipf.write(file_path, os.path.relpath(file_path, folder_path))

        # Serve the zip file as a downloadable response
        with open(zip_file_path, 'rb') as zipf:
            response = HttpResponse(zipf.read(), content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename={zip_file_name}'
        
        # Close the response before deleting the file
        response.close()

        # Delete the ZIP file from the server after the download
        os.remove(zip_file_path)

        # Set a success message
        messages.success(request, 'The Admit Cards folder has been successfully downloaded.')

        # Redirect back to the same page after download
        return response
    if request.method == 'POST' and 'single' in request.POST:
        cbse_no = request.POST.get("cbse_no")
        gene_check = check_generated_by_cbse_no(cbse_no, 'a', request.user)
        if gene_check[0]:
            file_path = os.path.join(folder_path, cbse_no + "_admit_card.png")
            if os.path.exists(file_path):
                with open(file_path, "rb") as admit_card:
                    response = HttpResponse(admit_card.read(), content_type="image/png")
                    response['Content-Disposition'] = f'attachment; filename={cbse_no}s_admit_card.png'
                response.close()
                messages.success(request, "Admin card downloaded successfully")
                return response
            else:
                messages.error(request, "Admit card not available for this CBSE No.")
        else:
            messages.error(request, gene_check[1])
    # Render the template for GET requests
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
        'Army': {'A': 'Army_A.png', 'B': 'Army_B.png', 'C': 'c_cert.jpg'},
        'Navy': {'A': 'Navy_A.png', 'B': 'Navy_B.png', 'C': 'c_cert.jpg'},
        'Air Force': {'A': 'Air_Force_A.png', 'B': 'Air_Force_B.png', 'C': 'c_cert.jpg'},
    }

    try:
        template_path = os.path.join(settings.MEDIA_ROOT, 'Template_images', template_filenames[student.Wing][student.Certificate_type])
        if student.Certificate_type == "B":
            cert_back_path = os.path.join(settings.MEDIA_ROOT, 'Template_images', 'B_cert_back.png')
        if student.Certificate_type == "C":
            cert_back_path = os.path.join(settings.MEDIA_ROOT, 'Template_images', 'C_cert_back.png')
    except KeyError:
        raise ValueError("Invalid Wing or Certificate Type.")
    cert_back = None  # Initialize cert_back
    template = cv2.imread(template_path)
    width, height = template.shape[1], template.shape[0]
    if student.Certificate_type == "B":
        cert_back = cv2.imread(cert_back_path)
    elif student.Certificate_type == "C":
        cert_back = cv2.imread(cert_back_path)
    elif student.Certificate_type == "A":
        cert_back = Image.fromarray(np.ones((height, width, 3), dtype=np.uint8) * 255)
    if isinstance(cert_back, np.ndarray):
        cert_back_pil = Image.fromarray(cv2.cvtColor(cert_back, cv2.COLOR_BGR2RGB))
    else:
        cert_back_pil = cert_back

    
    if template is None or cert_back is None:
        raise ValueError("Could not load the certificate template or back image.")
    # Convert the template image from OpenCV format (BGR) to PIL format (RGB)
    template_pil = Image.fromarray(cv2.cvtColor(template, cv2.COLOR_BGR2RGB))
    
    # Initialize ImageDraw object
    draw = ImageDraw.Draw(template_pil)

    # Load the font
    font_path = os.path.join(settings.MEDIA_ROOT, 'Template_images', 'Devnagri.ttf')  # Use regular font
    font_size = 15
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        raise ValueError("Could not load the specified font.")

    # Define text and their corresponding positions based on the certificate type
    if student.Certificate_type == "C":
        hindi_certificate_type=utility.translate_names("hi", student.Certificate_type)
        texts_with_positions = [
            (student.Unit, (141, 515)),
            (student.CBSE_No, (122, 422)),
            (student.Rank, (431, 394)),
            (student.Name, (141, 465)),
            (student.name_hindi, (128,444)),
            (student.fathers_name_hindi, (492, 450)),
            (student.DOB, (498, 515)),
            (student.Fathers_Name, (518, 470)),
            (student.Certificate_type, (491, 360)),
            (student.result.Grade,(464,638)),
            (student.certificate.Place, (141, 848)),
            (student.certificate.Date, (141, 906)),
            (student.Year, (210, 633)),
            (student.Year, (426, 710)),
            (student.Directorate, (224, 561)),
            (student.certificate.certificate_id, (500, 10)),
            (hindi_certificate_type,(444,321)),
            (student.result.Grade,(243, 710))
        ]
    else:
        hindi_certificate_type=utility.translate_names("hi", student.Certificate_type)
        texts_with_positions = [
            (student.Unit, (160, 423)),
            (student.CBSE_No, (160, 340)),
            (student.Rank, (470, 330)),
            (student.Name, (170, 386)),
            (student.name_hindi, (165,370)),
            (student.fathers_name_hindi, (515, 365)),
            (student.DOB, (530, 420)),
            (student.Fathers_Name, (555, 381)),
            (student.Certificate_type, (270, 595)),
            (student.certificate.Place, (170, 710)),
            (student.certificate.Date, (165, 750)),
            (student.Year, (295, 545)),
            (student.Year, (575, 595)),
            (student.Directorate, (255, 487)),
            (student.certificate.certificate_id, (510, 15)),
            (hindi_certificate_type,(435,545)),
            (student.result.Grade,(210,647))

        ]

    # Add text to the image with bold effect
    for text, position in texts_with_positions:
        if text:
            # Simulate bold by drawing the text multiple times with slight offsets
            x, y = position
            for offset in [(.2, 0), (-.2, 0), (0, .2), (0, -.2)]:
                draw.text((x + offset[0], y + offset[1]), str(text), font=font, fill=(0, 0, 0))
            draw.text((x, y), str(text), font=font, fill=(0, 0, 0))  # Draw the main text

    # Add the student's photo to the certificate

    if student.Certificate_type == "C":
        if student.Photo:
            try:
                insert_image_path = student.Photo.path
                insert_image = Image.open(insert_image_path)
                insert_image = insert_image.resize((130, 170))
                image_position = (595, 85)
                template_pil.paste(insert_image, image_position)
            except Exception as e:
                raise ValueError(f"Could not process the student's photo. Error: {e}, Photo Path: {insert_image_path}")
    else :
        if student.Photo:
            try:
                insert_image_path = student.Photo.path
                insert_image = Image.open(insert_image_path)
                insert_image = insert_image.resize((130, 130))
                image_position = (593, 40)
                template_pil.paste(insert_image, image_position)
            except Exception as e:
                raise ValueError(f"Could not process the student's photo. Error: {e}, Photo Path: {insert_image_path}")


    # Generate and insert QR code
    qr_image_path = generate_qr_code(student)
    if qr_image_path:
        try:
            qr_image = Image.open(qr_image_path)
            qr_image = qr_image.resize((120, 120))  # Resize QR code as needed
            qr_position = (45, 40)  # Set QR code position
            template_pil.paste(qr_image, qr_position)
        except Exception as e:
            raise ValueError(f"Could not process the QR code image. Error: {e}, QR Code Path: {qr_image_path}")

    # Save the final image
    output_dir = os.path.join(settings.MEDIA_ROOT, 'Certificates')
    os.makedirs(output_dir, exist_ok=True)
    final_image_path = os.path.join(output_dir, f'{student.CBSE_No}_certificate.png')
    final_back_image_path = os.path.join(output_dir, f'{student.CBSE_No}_back_certificate.png')

    try:
        template_pil.save(final_image_path)
        cert_back_pil.save(final_back_image_path)
        print(f"Certificate saved at: {final_image_path}")
    except Exception as e:
        raise ValueError(f"Could not save the certificate image. Error: {e}")

    return final_image_path

@login_required
def send_for_approval(request, cbse_no, page):
    _send_for_approval(cbse_no, request.user)
    return redirect('/Preview Admit Card/'+str(page)+"/")

def _send_for_approval(cbse_no, user):
    try:
        student = Student.objects.get(CBSE_No=cbse_no, clerk_id=Clerk.objects.get(user_id=user.id).id)
        student.rejection_reason = None
        student.admit_card_send_for_approval=True
        student.save()
    except Exception as e:
        print("Not able to send admit card for approval for: ", cbse_no, " due to error ", e)


@login_required
def bulk_approve_admit_card(request):
    cbse_no_list = request.POST.getlist("checkedBoxes[]")
    action = request.POST.get("action")
    page = request.POST.get("page")
    print(cbse_no_list, action, page)
    try:
        for cbse_no in cbse_no_list:
            if action == 'approve':
                if page == 'cert':
                    _approve_certificate(request, cbse_no)
                elif page == 'admit_card':
                    _approve_admit_card(cbse_no)
            elif action == 'reject':
                if page == 'cert':
                    _reject_certificate(request, cbse_no, "Bulk Rejected")
                elif page == 'admit_card':
                    _reject_admit_card(request, cbse_no, "Bulk Rejected")
            elif action == 'send':
                if page == 'cert':
                    _approve_certificate(request, cbse_no)
                elif page == 'admit_card':
                    _send_for_approval(cbse_no, request.user)
        return HttpResponse({"status": 200, "message": "success"}, content_type='application/json', status=200)
    except Exception as e:
        return HttpResponse({"status": 500, "message": "failed"}, content_type='application/json', status=200)

@login_required
def approve_admit_card(request, cbse_no, page):
    _approve_admit_card(cbse_no)
    return redirect('/Preview Admit Card/'+str(page)+"/")

def _approve_admit_card(cbse_no):
    try:
        print("Approving admit card for: ", cbse_no)
        student = Student.objects.get(CBSE_No=cbse_no)
        student.rejection_reason = None
        student.admit_card_approved = True
        student.save()
    except Exception as e:
        print("Unable to approve admit card for student with CBSE No. ", cbse_no, " due to exception: ", e)

@login_required
def reject_admit_card(request, cbse_no, page):
    if request.method == 'POST':
        _reject_admit_card(request, cbse_no, None)
    if "vareject" in request.POST:
        return HttpResponse({"status": 200, "message": "success"}, content_type='application/json', status=200)
    return redirect('/Preview Admit Card/'+str(page)+"/")

def _reject_admit_card(request, cbse_no, reject_reason):
    try:
        student = Student.objects.get(CBSE_No=cbse_no)
        reason = request.POST.get('rejection_reason')
        student.admit_card_approved = False
        student.admit_card_send_for_approval=False
        student.rejection_reason = reject_reason if reject_reason is not None else reason
        student.save()
    except Exception as e:
        print("Exception occurred while rejection:: ", e)
        messages.error(request, "Error occurred while rejecting")

@login_required
def Register_Students(request):
    if request.user.has_perm('home.can_create_new_candidates'):
        try:
            clerk = Clerk.objects.get(user=request.user)  # Get the Clerk associated with the user
            if clerk.certificate_no_start == -1:
                messages.info(request, "Please provide the range for certificate number")
                return render(request, "clerk/Register_Students.html")
            if request.method == 'POST':
                certificate_type=request.POST.get('certificate_type')
                wing=request.POST.get('wing')
                data_file = request.FILES.get('excel_file')
                photos_folder = request.FILES.getlist('photos_folder')
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
                        student_data["name_hindi"]=utility.translate_names("hi", student_data["Name"])
                        student_data["fathers_name_hindi"]=utility.translate_names("hi", student_data["Fathers_Name"])
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
        except Exception as e:
            print("Exception is : ", e)
            messages.info(request, "Some error occurred, Please try again")
            return render(request, "clerk/Register_Students.html")
    else:
        return redirect('/index/')

@login_required
def Rejected_Admit_Cards(request, page):
    if request.user.has_perm('home.can_view_rejected_applications'):
        # Query to get students with rejected admit cards
        current_page = int(page)
        user = request.user
        rejected_students=[]
        if user.groups.filter(name='Director_General').exists():
            director_general_id = Director_General.objects.get(user_id=user.id).id
            rejected_students = Student.objects.filter(admit_card_approved=False, rejection_reason__isnull=False, director_general_id=director_general_id).order_by('id')
        elif user.groups.filter(name='Brigadier').exists():
            brigadier_id = Brigadier.objects.get(user_id=user.id).id
            rejected_students = Student.objects.filter(admit_card_approved=False, rejection_reason__isnull=False, brigadier_id=brigadier_id).order_by('id')
        elif user.groups.filter(name='Colonel').exists():
            colonel_id = Colonel.objects.get(user_id=user.id).id
            rejected_students = Student.objects.filter(admit_card_approved=False, rejection_reason__isnull=False, colonel_id=colonel_id).order_by('id')
        elif user.groups.filter(name='Clerk').exists():
            clerk_id = Clerk.objects.get(user_id=user.id).id
            rejected_students = Student.objects.filter(admit_card_approved=False, rejection_reason__isnull=False, clerk_id=clerk_id).order_by('id')
        else:
            messages.error(request, "You do not have permission to perform this action.")
            return redirect('/user/')
        
        total_pages = len(rejected_students) // 10 if len(rejected_students) % 10 == 0 else (len(rejected_students) // 10) + 1
        if total_pages == 0:
            total_pages = 1
        if current_page == 0:
            current_page = 1
        elif current_page > total_pages:
            current_page = total_pages
        offset = ((current_page-1) * 10)
        last_record_index = (current_page * 10)
        if last_record_index > len(rejected_students):
            last_record_index = len(rejected_students)
        
        rejected_students = rejected_students[offset: last_record_index]
        # Pass the data to the template
        context = {
            'rejected_students': rejected_students,
            'students_json': json.dumps(list([str(model_to_dict(i)) for i in rejected_students]), cls=DjangoJSONEncoder),
            'current_page': current_page,
            'total_pages': total_pages,
            'disable_prev': current_page == 1,
            'disable_next': current_page >= total_pages,
            'prev_page': current_page - 1,
            'next_page': current_page + 1,
            'page_range': range(1, total_pages+1)
        }
        return render(request, "clerk/Rejected_Admit_Cards.html", context)
    else:
        return redirect('/index/')

@login_required
def Student_Details(request, page):
    view_students = Student.objects.none()  # Default to an empty queryset
    current_page = int(page)
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

    total_pages = len(view_students) // 10 if len(view_students) % 10 == 0 else (len(view_students) // 10) + 1
    if total_pages == 0:
        total_pages = 1
    if current_page == 0:
        current_page = 1
    elif current_page > total_pages:
        current_page = total_pages
    offset = ((current_page-1) * 10)
    last_record_index = (current_page * 10)
    if last_record_index > len(view_students):
        last_record_index = len(view_students)
    
    view_students = view_students[offset: last_record_index]
    context = {
        'students': view_students,
        'students_json': json.dumps(list([str(model_to_dict(i)) for i in view_students]), cls=DjangoJSONEncoder),
        'current_page': current_page,
        'total_pages': total_pages,
        'disable_prev': current_page == 1,
        'disable_next': current_page >= total_pages,
        'prev_page': current_page - 1,
        'next_page': current_page + 1,
        'page_range': range(1, total_pages+1)
    }
    return render(request, "clerk/Student_Details.html", context)

@login_required
def All_Students_Previewed(request):
    return render(request,"/All Students Previewed/")

@login_required
def update_student(request, page):
    if request.method == 'POST':
        student = get_object_or_404(Student, id=request.POST.get("id"))
        # Get data from POST request and handle empty values
        def get_value(field_name, default=None):
            value = request.POST.get(field_name, default)
            if value == '':
                return None
            return value
        
        pagee = get_value("page")
        # Updating fields
        student.Name = get_value('Name')
        student.name_hindi = get_value("Name_Hindi")
        student.Fathers_Name = get_value('Fathers_Name')
        student.fathers_name_hindi = get_value("Fathers_Name_Hindi")
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
        print(pagee)
        # Save the student object
        
        generate_admit_card(student)
        if student.certificate_id is not None and pagee=='cert_modify':
            generate_certificate_action(request, student.CBSE_No, page)
        else:
            student.certificate_id = None
        student.save()
            
        if pagee == 'result':
            return redirect('/Rejected Admit Cards/'+str(page)+"/")
        elif pagee == 'student':
            return redirect('/Student Details/'+str(page)+"/")  # Redirect after saving
        elif pagee == 'certificate':
            
            return redirect("/rejected-certificate/"+str(page)+"/")
        elif pagee == 'admit_card':
            return HttpResponse({"status": 200, "message": "success"}, content_type='application/json', status=200)
        elif pagee == 'cert_modify':
            return HttpResponse({"status": 200, "message": "success"}, content_type='application/json', status=200)


    return render(request, 'clerk/Student_Details.html', {'student': student})

@login_required
def search_student(request, page):
    student = None
    context = None
    if 'cbse_no' in request.GET and request.GET.get('cbse_no'):
        cbse_no = request.GET.get('cbse_no')
        student = get_object_or_404(Student, CBSE_No=cbse_no)
        context = {
            'students': [student],
            'students_json': json.dumps([str(model_to_dict(student))], cls=DjangoJSONEncoder),
            'current_page': 1
        }
        return render(request, 'clerk/Student_Details.html', context)
    else:
        return redirect("/Student Details/"+str(page)+"/")


@login_required
def search_result(request, page):
    cbse_no = request.POST.get("cbse_no")
    if cbse_no:
        if request.user.groups.filter(name='Colonel').exists():
            results_data = Student.objects.filter(result__isnull=False, colonel=Colonel.objects.get(user_id=request.user.id), CBSE_No = cbse_no).order_by('id')
        elif request.user.groups.filter(name='Clerk').exists():
            results_data = Student.objects.filter(result__isnull=False, clerk=Clerk.objects.get(user_id=request.user.id), CBSE_No = cbse_no).order_by('id')
        elif request.user.groups.filter(name='Brigadier').exists():
            results_data = Student.objects.filter(result__isnull=False, brigadier=Brigadier.objects.get(user_id=request.user.id), CBSE_No = cbse_no).order_by('id')
        elif request.user.groups.filter(name='Director_General').exists():
            results_data = Student.objects.filter(result__isnull=False, director_general=Director_General.objects.get(user_id=request.user.id), CBSE_No = cbse_no).order_by('id')
        return_data = [{"id": student.id,"student_id": student.CBSE_No, "result": model_to_dict(student.result), "student_name": student.Name, "college": student.School_College_Class, "unit": student.Unit,"rank": student.Rank, "p_1_total": student.result.Paper1_T, "p_2_total": student.result.Paper2_T, "p_3_total": student.result.Paper3_W, "p_4_total": student.result.Paper4_T, "cert_generated": student.certificate_id != None} for student in results_data]
        serialized_return_data = json.dumps(list(return_data), cls=DjangoJSONEncoder)
        return render(request, "clerk/view_results.html", {"result_data": return_data, "serialized_result_data": serialized_return_data, 'current_page': 1 })
    else:
        return redirect("/view-results/"+str(page)+"/")
    
@login_required
def search_admit_card(request, page):
    cbse_no = request.GET.get("cbse_no")
    pending_students = []
    if request.user.groups.filter(name='Colonel').exists():
        pending_students = Student.objects.filter(admit_card_approved=False, CBSE_No = cbse_no, rejection_reason=None, admit_card_send_for_approval=True, colonel_id=Colonel.objects.filter(user_id=request.user.id)[0].id).order_by('id')
    elif request.user.groups.filter(name='Clerk').exists():
        pending_students = Student.objects.filter(admit_card_approved=False, CBSE_No = cbse_no, rejection_reason=None, admit_card_send_for_approval=False, clerk_id=Clerk.objects.filter(user_id=request.user.id)[0].id).order_by('id')
        # pending_students = Student.objects.filter(clerk_id=Clerk.objects.filter(user_id=request.user.id)[0].id).order_by('id')
    else:
        messages.error(request, "You do not have permission to perform this action.")
        return redirect('/user/')
    certificates = []
    for student in pending_students:
        root_cert_path = None
        # Generate the admit card if it hasn't been generated yet
        if not student.admit_card_generated:
            admit_card_image_path = generate_admit_card(student)
            student.admit_card_generated = True
            root_cert_path = admit_card_image_path
            student.save()
        else:
            admit_card_image_path = os.path.join(settings.MEDIA_URL, 'Admit_Cards', f'{student.CBSE_No}_admit_card.png')
            root_cert_path = settings.MEDIA_ROOT + "/"+"/".join(admit_card_image_path.split("/")[2:])
        blob_image = base64.b64encode(open(root_cert_path, "rb").read()).decode()
        certificates.append(blob_image)
    print("The number of certs", len(certificates))
    context = {
        "certificates": json.dumps(certificates, cls=DjangoJSONEncoder),   
        'pending_students': pending_students,
    }
    return render(request, "clerk/Preview_Admit_Card.html", context)

@login_required
def search_certificate(request, page):
    cbse_no = request.GET.get("cbse_no")
    pending_students=[]
    if request.user.groups.filter(name='Director_General').exists():
        director_general_id = Director_General.objects.get(user_id=request.user.id).id
        pending_students = Student.objects.filter(
            certificate__Approval_stage=3,
            certificate__Rejected_reason=None,
            director_general_id=director_general_id,
            certificate__certificate_generated=True,
            CBSE_No = cbse_no
        ).order_by('id')

    elif request.user.groups.filter(name='Brigadier').exists():
        brigadier_id = Brigadier.objects.get(user_id=request.user.id).id
        pending_students = Student.objects.filter(
            certificate__Approved=False,
            certificate__Approval_stage=2,
            certificate__Rejected_reason=None,
            brigadier_id=brigadier_id,
            certificate__certificate_generated=True,
            CBSE_No = cbse_no
        ).order_by('id')

    elif request.user.groups.filter(name='Colonel').exists():
        colonel_id = Colonel.objects.get(user_id=request.user.id).id
        pending_students = Student.objects.filter(
            certificate__Approved=False,
            certificate__Approval_stage=1,
            certificate__Rejected_reason=None,
            colonel_id=colonel_id,
            certificate__certificate_generated=True,
            CBSE_No = cbse_no
        ).order_by('id')
    elif request.user.groups.filter(name='Clerk').exists():
        clerk_id = Clerk.objects.get(user_id=request.user.id).id
        pending_students = Student.objects.filter(
            certificate__Approved=False,
            certificate__Approval_stage=0,
            certificate__Rejected_reason=None,
            clerk_id=clerk_id,
            certificate__certificate_generated=True,
            CBSE_No = cbse_no
        ).order_by('id')
    else:
        messages.error(request, "You do not have permission to perform this action.")
        return redirect('/user/')
    certificates = []
    for student in pending_students:
        certificate_image_path = None
        if student.certificate_id is not None:
            certificate_image_path = student.certificate.certificate_path
            if not os.path.exists(certificate_image_path):
                certificate_image_path = generate_certificate(student)
                certi = student.certificate
                certi.certificate_path = certificate_image_path
                certi.save()
        else:
            certificate_image_path = generate_certificate(student)
            certi = student.certificate
            certi.certificate_path = certificate_image_path
            certi.save()
        blob_image = base64.b64encode(open(certificate_image_path, "rb").read()).decode()
        certificates.append(blob_image) 
    
    context = {
        "certificates": json.dumps(certificates, cls=DjangoJSONEncoder),   
        'pending_students': pending_students
    }
    return render(request, "clerk/Preview_Certificates.html", context)
    

@login_required
def reject_certificate(request, cbse_no, page):
    print("In reject certificate", cbse_no, page)
    if request.method == 'POST':
        _reject_certificate(request, cbse_no, None)
    if "vareject" in request.POST:
        return HttpResponse({"status": 200, "message": "success"}, content_type='application/json', status=200)
    return redirect('/Preview Certificates/'+str(page)+"/")

def _reject_certificate(request, cbse_no, reject_reason):
    try:
        student = get_object_or_404(Student, CBSE_No=cbse_no)
        reason = request.POST.get('rejection_reason')
        certificate=student.certificate
        certificate.Approved = False
        certificate.Approval_stage=0
        certificate.Rejected_reason = reject_reason if reject_reason is not None else reason
        certificate.Rejected_by=request.user.groups.first().name + ": " + request.user.username
        certificate.save()
        student.save()
    except Exception as e:
        print("Some exception occurred: ", e)
        messages.error(request, "Some error occurred")

@login_required
def rejected_certificates(request, page):
    try:
        current_page = int(page)
        user = request.user
        rejected_students=[]
        if user.groups.filter(name='Director_General').exists():
            director_general_id = Director_General.objects.get(user_id=user.id).id
            rejected_students = Student.objects.filter(certificate__Approved=False, certificate__Rejected_by__isnull=False, director_general_id=director_general_id).order_by('id')
        elif user.groups.filter(name='Brigadier').exists():
            brigadier_id = Brigadier.objects.get(user_id=user.id).id
            rejected_students = Student.objects.filter(certificate__Approved=False, certificate__Rejected_by__isnull=False, brigadier_id=brigadier_id).order_by('id')
        elif user.groups.filter(name='Colonel').exists():
            colonel_id = Colonel.objects.get(user_id=user.id).id
            rejected_students = Student.objects.filter(certificate__Approved=False, certificate__Rejected_by__isnull=False, colonel_id=colonel_id).order_by('id')
        elif user.groups.filter(name='Clerk').exists():
            clerk_id = Clerk.objects.get(user_id=user.id).id
            rejected_students = Student.objects.filter(certificate__Approved=False, certificate__Rejected_by__isnull=False, clerk_id=clerk_id).order_by('id')
        else:
            messages.error(request, "You do not have permission to perform this action.")
            return redirect('/user/')
        total_pages = len(rejected_students) // 10 if len(rejected_students) % 10 == 0 else (len(rejected_students) // 10) + 1
        if total_pages == 0:
            total_pages = 1
        if current_page == 0:
            current_page = 1
        elif current_page > total_pages:
            current_page = total_pages
        offset = ((current_page-1) * 10)
        last_record_index = (current_page * 10)
        if last_record_index > len(rejected_students):
            last_record_index = len(rejected_students)
        
        rejected_students = rejected_students[offset: last_record_index]
        context={
            "certificate_list": rejected_students,
            'students_json': json.dumps(list([str(model_to_dict(i)) for i in rejected_students]), cls=DjangoJSONEncoder),
            'current_page': current_page,
            'total_pages': total_pages,
            'disable_prev': current_page == 1,
            'disable_next': current_page >= total_pages,
            'prev_page': current_page - 1,
            'next_page': current_page + 1,
            'page_range': range(1, total_pages+1)
        }
        return render(request, "clerk/rejected_certificates.html", context)
    except Exception as e:
        print("Unable to get rejected certificate list: ", e)
@login_required
def approve_cert_no_red(request, cbse_no, page):
    _approve_certificate(request, cbse_no)
    return HttpResponse({"status": 200, "message": "success"}, content_type='application/json', status=200)

@login_required
def approve_certificate(request, cbse_no, page):
   _approve_certificate(request, cbse_no)
   return redirect('/Preview Certificates/'+str(page)+"/")

def _approve_certificate(request, cbse_no):
   if request.user.groups.filter(name='Clerk').exists():
       student = get_object_or_404(Student, CBSE_No=cbse_no)
       certificate = student.certificate
       certificate.Approval_stage = 1
       certificate.save()
   elif request.user.groups.filter(name='Colonel').exists():
       student = get_object_or_404(Student, CBSE_No=cbse_no)
       certificate = student.certificate
       certificate.Approval_stage = 2
       if(student.Certificate_type=='A') :
           certificate.Approved = True
       certificate.save()
   elif request.user.groups.filter(name='Brigadier').exists():
       student = get_object_or_404(Student, CBSE_No=cbse_no)
       certificate = student.certificate
       certificate.Approval_stage = 3
       if(student.Certificate_type=='B') :
           certificate.Approved = True
       certificate.save()
   else :
       student = get_object_or_404(Student, CBSE_No=cbse_no)
       certificate = student.certificate
       certificate.Approved = True
       certificate.save()

@login_required
def Download_Admit_Card(request):
    if request.method == 'POST':
        cbse_no = request.POST.get('cbse_no')
        try:
            student = Student.objects.get(CBSE_No=cbse_no)

            # Assuming the admit card is stored in a folder within MEDIA_ROOT
            admit_card_path = os.path.join(settings.MEDIA_ROOT, 'Admit_Cards', f'{student.CBSE_No}.pdf')

            if os.path.exists(admit_card_path):
                with open(admit_card_path, 'rb') as admit_card_file:
                    response = HttpResponse(admit_card_file.read(), content_type='application/pdf')
                    response['Content-Disposition'] = f'attachment; filename="{student.CBSE_No}_Admit_Card.pdf"'
                    return response
            else:
                messages.error(request, 'Admit Card not found.')
                return redirect('Download_Admit_Card')
        
        except Student.DoesNotExist:
            messages.error(request, f'Student with CBSE No. {cbse_no} not found.')
            return redirect('Download_Admit_Card')

    return render(request, 'clerk/Download_Admit_Card.html')

def get_admit_card(request, page_type, cbse_no):
    try:
        response = None
        data = None
        if cbse_no and page_type:
            if page_type == 'cert':
                pending_students=[]
                if request.user.groups.filter(name='Director_General').exists():
                    director_general_id = Director_General.objects.get(user_id=request.user.id).id
                    pending_students = Student.objects.filter(
                        CBSE_No=cbse_no,
                        certificate__Approval_stage=3,
                        certificate__Rejected_reason=None,
                        director_general_id=director_general_id,
                        certificate__certificate_generated=True
                    ).order_by('id')

                elif request.user.groups.filter(name='Brigadier').exists():
                    brigadier_id = Brigadier.objects.get(user_id=request.user.id).id
                    pending_students = Student.objects.filter(
                        CBSE_No=cbse_no,
                        certificate__Approved=False,
                        certificate__Approval_stage=2,
                        certificate__Rejected_reason=None,
                        brigadier_id=brigadier_id,
                        certificate__certificate_generated=True
                    ).order_by('id')

                elif request.user.groups.filter(name='Colonel').exists():
                    colonel_id = Colonel.objects.get(user_id=request.user.id).id
                    pending_students = Student.objects.filter(
                        CBSE_No=cbse_no,
                        certificate__Approved=False,
                        certificate__Approval_stage=1,
                        certificate__Rejected_reason=None,
                        colonel_id=colonel_id,
                        certificate__certificate_generated=True
                    ).order_by('id')
                elif request.user.groups.filter(name='Clerk').exists():
                    clerk_id = Clerk.objects.get(user_id=request.user.id).id
                    pending_students = Student.objects.filter(
                        CBSE_No=cbse_no,
                        certificate__Approved=False,
                        certificate__Approval_stage=0,
                        certificate__Rejected_reason=None,
                        clerk_id=clerk_id,
                        certificate__certificate_generated=True
                    ).order_by('id')
                else:
                    messages.error(request, "You do not have permission to perform this action.")
                    return redirect('/user/')
                if pending_students.exists():
                    student = pending_students[0]
                    certificate_image_path = None
                    if student.certificate_id is not None:
                        certificate_image_path = student.certificate.certificate_path
                        if not os.path.exists(certificate_image_path):
                            certificate_image_path = generate_certificate(student)
                            certi = student.certificate
                            certi.certificate_path = certificate_image_path
                            certi.save()
                    else:
                        certificate_image_path = generate_certificate(student)
                        certi = student.certificate
                        certi.certificate_path = certificate_image_path
                        certi.save()
                    blob_image = base64.b64encode(open(certificate_image_path, "rb").read()).decode()
                    data = {
                        "status": 200,
                        "message": "Success",
                        "data": {
                            "cbse_no": cbse_no,
                            "image": blob_image
                        }
                    }
                    
                    response = HttpResponse(data, content_type='application/json', status=200)
                else:
                    data = {
                        "status": 400,
                        "message": "No Student found",
                    }
            elif page_type == 'admit_card':
                pending_students = []
                if request.user.groups.filter(name='Colonel').exists():
                    pending_students = Student.objects.filter(CBSE_No=cbse_no, admit_card_approved=False, rejection_reason=None, admit_card_send_for_approval=True, colonel_id=Colonel.objects.filter(user_id=request.user.id)[0].id).order_by('id')
                elif request.user.groups.filter(name='Clerk').exists():
                    pending_students = Student.objects.filter(CBSE_No=cbse_no, admit_card_approved=False, rejection_reason=None, admit_card_send_for_approval=False, clerk_id=Clerk.objects.filter(user_id=request.user.id)[0].id).order_by('id')
                    # pending_students = Student.objects.filter(clerk_id=Clerk.objects.filter(user_id=request.user.id)[0].id).order_by('id')
                else:
                    messages.error(request, "You do not have permission to perform this action.")
                    return redirect('/user/')
                if pending_students.exists():
                    root_cert_path = None
                    student = pending_students[0]
                    # Generate the admit card if it hasn't been generated yet
                    if not student.admit_card_generated:
                        admit_card_image_path = generate_admit_card(student)
                        student.admit_card_generated = True
                        root_cert_path = admit_card_image_path
                        student.save()
                    else:
                        admit_card_image_path = os.path.join(settings.MEDIA_URL, 'Admit_Cards', f'{student.CBSE_No}_admit_card.png')
                        root_cert_path = settings.MEDIA_ROOT + "/"+"/".join(admit_card_image_path.split("/")[2:])
                    blob_image = base64.b64encode(open(root_cert_path, "rb").read()).decode()
                    data = {
                        "status": 200,
                        "message": "Success",
                        "data": {
                            "cbse_no": cbse_no,
                            "image": blob_image
                        }
                    }
                else:
                    data = {
                        "status": 400,
                        "message": "No Student found",
                    }
            else:
                data = {
                    "status": 400,
                    "message": "Failed",
                }
        else:
            data = {
                "status": 400,
                "message": "Failed",
            }
    except Exception as e:
        print("Some exception occurred", e) 
        messages.error(request, "Some error occurred")
        data = {
            "status": 500,
            "message": "Failed",
        }
    data = json.dumps(data, cls=DjangoJSONEncoder)
    response = HttpResponse(data, content_type='application/json', status=200)
    return response
@login_required  
def add_certificate_range(request):
    if request.method == 'POST':
       
        certificate_no_start = request.POST.get('certificate_number_start')
        certificate_no_end = request.POST.get('certificate_number_end')

        # Assuming user has a related Profile model to store certificate numbers
        try:
            clerk = Clerk.objects.get(user=request.user)
        except Clerk.DoesNotExist:
            messages.error(request, "Clerk profile not found.")
            return redirect('Register_Students')

        clerk.certificate_no_start = certificate_no_start
        clerk.certificate_no_end = certificate_no_end
        clerk.certificate_no_current=certificate_no_start
        clerk.save()

        return redirect('Register_Students')

    return render(request, 'Register_Students.html')