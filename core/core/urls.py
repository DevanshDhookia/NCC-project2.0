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
    path('accounts/login/',SignIn,name='AccountSignIn'),
    path('register/',register,name='register'),
    path('user-logout/', user_logout, name='logout'),
    path('index/',index,name='index'),
    path('clerk/',clerk_page,name='clerk'),
    path('Preview Admit Card/',Preview_Admit_Card,name='Preview_Admit_Card'),
    path('Print Admit Cards/',Print_Admit_Cards,name='Print_Admit_Cards'),
    path('Register Students/',Register_Students,name='Register_Students'),
    path('Add Result/',Add_Result,name='Add_Result'),
    path('Rejected Admit Cards/',Rejected_Admit_Cards,name='Rejected_Admit_Cards'),
    path('Student Details/',Student_Details,name='Student_Details'),
    path('All Students Previewed/',All_Students_Previewed,name='All_Students_Previewed'),
    path('approve_admit_card/<str:cbse_no>/', approve_admit_card, name='approve_admit_card'),
    path('can_send_admit_card_for_approval/<str:cbse_no>/', approve_admit_card, name='approve_admit_card'),
    path('reject_admit_card/<str:cbse_no>/', reject_admit_card, name='reject_admit_card'),
    path('search/', search_student, name='search_student'),
    path('update/', update_student, name='update_student'),
    path('send_for_approval/<str:cbse_no>/', send_for_approval, name='send_for_approval'),

    path("admin/", admin.site.urls),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)