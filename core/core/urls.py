"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from home.views import *
from django.conf.urls.static import static
from django.conf import settings
from home.views import *



urlpatterns = [
    path('',home,name='home'),
    path('contact/',contact,name='contact'),
    path('SignIn/',SignIn,name='SignIn'),
    path('change-password/',change_password,name='change_password'),
    path('forgot-password/',forgot_password,name='forgot_password'),
    path('accounts/login/',SignIn,name='AccountSignIn'),
    path('register/',register,name='register'),
    path('generate-otp/',generate_otp,name='generate_otp'),
    path('user-logout/', user_logout, name='logout'),
    path('index/',index,name='index'),
    path('user/',clerk_page,name='clerk_p'),
    path('user/<str:user_id>',clerk_page,name='clerk'),
    path('Preview Admit Card/<int:page>/',Preview_Admit_Card,name='Preview_Admit_Card'),
    path('Preview Certificates/<int:page>/',Preview_Certificates,name='Preview_Certificates'),
    path('Print Admit Cards/',Print_Admit_Cards,name='Print_Admit_Cards'),
    path('Register Students/',Register_Students,name='Register_Students'),
    path('Add Result/',Add_Result,name='Add_Result'),
    path('add-result-data/',add_result_data,name='Add_Result_file'),
    path('view-results/<int:page>/',results,name='view-results'),
    path('update-results/<int:page>/',results,name='update-results'),
    path('Rejected Admit Cards/<int:page>/',Rejected_Admit_Cards,name='Rejected_Admit_Cards'),
    path('Student Details/<int:page>/',Student_Details,name='Student_Details'),
    path('All Students Previewed/',All_Students_Previewed,name='All_Students_Previewed'),
    path('approve_admit_card/<str:cbse_no>/<int:page>/', approve_admit_card, name='approve_admit_card'),
    path('bulk_action/', bulk_approve_admit_card, name='bulk_action'),
    path('can_send_admit_card_for_approval/<str:cbse_no>/', approve_admit_card, name='approve_admit_card'),
    path('reject_admit_card/<str:cbse_no>/<int:page>/', reject_admit_card, name='reject_admit_card'),
    path('search/<int:page>/', search_student, name='search_student'),
    path('search-result/<int:page>/', search_result, name='search_result'),
    path('search-admit-card/<int:page>/', search_admit_card, name='search_result'),
    path('search-certificate/<int:page>/', search_certificate, name='search_result'),
    path('update/<int:page>/', update_student, name='update_student'),
    path('send_for_approval/<str:cbse_no>/<int:page>/', send_for_approval, name='send_for_approval'),
    path('generate_certificate/<str:cbse_no>/<int:page>/', generate_certificate_action, name="generate_certificate"),
    path('approve_certificate/<str:cbse_no>/<int:page>/', approve_certificate, name='approve_certificate'),
    path('reject_certificate/<str:cbse_no>/<int:page>/', reject_certificate, name='reject_certificate'),
    path('rejected-certificate/<int:page>/', rejected_certificates, name='rejected_certificate'),
    path('print-certificate/', print_certificate, name='print_certificate'),
    path('download-admit-card/', Download_Admit_Card, name='Download_Admit_Card'),
    # Other paths...
    path("admin/", admin.site.urls),
    path('404/', custom_404_view, name='custom_404'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)