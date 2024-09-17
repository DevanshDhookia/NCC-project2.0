from models import Student, Certificate, Result, Director_General, Brigadier
from models import Colonel, Clerk, OTP
from django.contrib.auth.models import User

def delete_data():
    users = User.objects.filter(is_superuser = False)
    for user in users:
        if user.id != 2:
            user.delete()
    
    certs = Certificate.objects.all()
    for cert in certs:
        cert.delete()
    
    results = Result.objects.all()
    for result in results:
        result.delete()
        
    students = Student.objects.all()
    for student in students:
        student.delete()
        
    otps = OTP.objects.all()
    for otp in otps:
        otp.delete()

if __name__ == '__main__':
    delete_data()
    