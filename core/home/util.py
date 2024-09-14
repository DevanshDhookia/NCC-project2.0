from django.contrib.auth.models import User
from .models import OTP
from django.conf import settings
from random import randint
from datetime import datetime, timedelta

class Util():
    def generate_and_save_otp(self, username):
        try:
            otp_length = settings.OTP_LENGTH
            range_start = 10**(otp_length-1)
            range_end = (10**otp_length)-1
            otp = str(randint(range_start, range_end))
            curr_time = datetime.now()
            expiry_time = curr_time + timedelta(minutes=10)
            ottp = OTP.objects.filter(username=username)
            if ottp:
                ottp = ottp[0]
                ottp.otp = otp
                ottp.expiry_time = expiry_time
                ottp.save()
            else:
                ottp = OTP.objects.create(
                    username=username,
                    otp=otp,
                    expiry_time = expiry_time
                )
            return True, otp
        except Exception as e:
            print("Exception occurred while generating otp", e)
            return False, ""
        
    def validate_otp(self, username, otp):
        try:
            ottp = OTP.objects.filter(username = username)
            if ottp:
                ottp = ottp[0]
                print("otp from db: ", ottp.otp, " otp from request: ", otp)
                if otp != ottp.otp:
                    return False, "OTP does not match"
                else:
                    print(datetime.now(), ottp.expiry_time)
                    if ottp.expiry_time < datetime.now():
                        return False, "OTP expired"
                    else:
                        ottp.delete()
                        return True, ""
            else:
                return False, "OTP not found for username"
        except Exception as e:
            print("Unable to validate otp: ", e)
            return False, "Unable to validate"
                    