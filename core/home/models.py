from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

class Director_General(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

class Brigadier(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    director_general = models.ForeignKey(Director_General, on_delete=models.CASCADE, related_name="brigadiers", default=1)  # Assuming `Director_General` with ID 1 exists


class Colonel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    brigadier = models.ForeignKey(Brigadier, on_delete=models.CASCADE, related_name="colonels", default=1)  # Replace 1 with the appropriate ID

class Clerk(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    colonel = models.ForeignKey(Colonel, on_delete=models.CASCADE, related_name="clerks")
    certificate_no_start= models.IntegerField(null=True,default=-1)
    certificate_no_end=models.IntegerField(null=True,default=-1)
    certificate_no_current=models.IntegerField(null=True,default=-1)


class BonusMarksCategories(models.Model):
    type = models.CharField(max_length=100, null=True)
    percentage = models.IntegerField(default=0)

class Result(models.Model):
    Parade_attendance=models.IntegerField()
    Paper1_W = models.FloatField()
    Paper1_P = models.FloatField()
    Paper1_T = models.FloatField()
    Paper2_W = models.FloatField()
    Paper2_P = models.FloatField()
    Paper2_T = models.FloatField()
    Paper3_W = models.FloatField()
    Paper4_W = models.FloatField()
    Paper4_P = models.FloatField()
    Paper4_T = models.FloatField()
    bonus_marks_cat = models.ForeignKey(BonusMarksCategories, on_delete=models.CASCADE, related_name="bonus_marks", default=0, blank=True)
    Bonus_marks=models.FloatField(default=0)
    Final_total=models.FloatField()
    Pass=models.BooleanField(default=False)
    Grade=models.CharField(max_length=100, null=True)
    
class Certificate(models.Model):
    certificate_id=models.CharField(max_length=15, unique=True)
    certificate_generated=models.BooleanField(default=False)
    Date=models.DateField(max_length=15,null=True)
    Approval_stage=models.CharField(max_length=15,null=True)
    Rejected_by=models.CharField(max_length=100,null=True)
    Rejected_reason=models.CharField(max_length=100,null=True)
    Approved=models.BooleanField(default=False)
    Qr_code= models.ImageField(upload_to='qr_code/', null=True, blank=True)
    Generation_date=models.DateField(null=True)
    Place=models.CharField(max_length=100,null=True)
    certificate_path=models.CharField(max_length=200, null=True)



class Student(models.Model):
    CBSE_No = models.CharField(max_length=15, unique=True)
    Name = models.CharField(max_length=100)
    name_hindi = models.TextField(max_length=100, null=True)
    DOB = models.CharField(max_length=20)
    Fathers_Name = models.CharField(max_length=100)
    fathers_name_hindi = models.TextField(max_length=100, null=True)
    School_College_Class = models.CharField(max_length=100)
    Home_Address = models.CharField(max_length=100)
    Admit_Card_No = models.IntegerField()
    Unit = models.CharField(max_length=50)
    Rank = models.CharField(max_length=50)
    Year_of_passing_B_Certificate = models.CharField(max_length=10, default='N/A')
    Fresh_Failure = models.CharField(max_length=10)
    Attendance_1st_year = models.IntegerField(null=True, blank=True)
    Attendance_2nd_year = models.IntegerField(null=True, blank=True)
    Attendance_3rd_year = models.IntegerField(null=True, blank=True)
    Name_of_camp_attended_1 = models.CharField(max_length=100, null=True, default='N/A')
    Date_camp_1 = models.CharField(max_length=10, null=True, default='N/A')
    Location_camp_1 = models.CharField(max_length=100, default='N/A', null=True)
    Name_of_camp_attended_2 = models.CharField(max_length=100, default='N/A', null=True)
    Date_camp_2 = models.CharField(max_length=10, null=True, default='N/A')
    Location_camp_2 = models.CharField(max_length=100, null=True, default='N/A')
    Photo = models.ImageField(upload_to='student_photos/', null=True, blank=True)
    Wing =models.CharField(max_length=10, null=True, default='N/A')
    Certificate_type=models.CharField(max_length=10, null=True, default='N/A')
    admit_card_generated = models.BooleanField(default=False)
    admit_card_send_for_approval=models.BooleanField(default=False)
    admit_card_approved = models.BooleanField(default=False)
    rejection_reason = models.TextField(null=True, blank=True)
    clerk = models.ForeignKey(Clerk, on_delete=models.CASCADE, related_name="students", null=True, blank=True)
    colonel = models.ForeignKey(Colonel, on_delete=models.CASCADE, null=True, blank=True)
    brigadier = models.ForeignKey(Brigadier, on_delete=models.CASCADE, null=True, blank=True)
    director_general = models.ForeignKey(Director_General, on_delete=models.CASCADE, null=True, blank=True)
    sent_for_approval = models.BooleanField(default=False)
    result=models.ForeignKey(Result, on_delete=models.CASCADE, related_name="results", null=True, blank=True)
    certificate=models.ForeignKey(Certificate, on_delete=models.CASCADE, related_name="certificates", null=True, blank=True)
    Year = models.IntegerField(default=24, null=True)
    # int(str(datetime.now().year)[-2:])
    Directorate=models.CharField(max_length=100, null=True, default='Kanpur')

class OTP(models.Model):
    username = models.CharField(max_length = 100)
    otp = models.CharField(max_length=6)
    expiry_time = models.DateTimeField(null = False)