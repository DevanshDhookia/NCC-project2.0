import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class SMTPManager():
    sender = "mahia020005@gmail.com"


    def send_email(self, username, receiver, otp):
        mail_sent = False
        msg = MIMEMultipart('alternative')
        msg["From"] = self.sender
        msg["To"] = receiver
        msg["Subject"] = "donotreply@NCC, Otp verification for user"
        message = "Hi " +username+", Your otp for verification of the user is " + otp + ". This will be valid only for 10 minutes"
        mail_server = smtplib.SMTP('smtp.gmail.com', 587)
        msg.attach(MIMEText(message))
        try:
            mail_server.ehlo()
            mail_server.starttls()
            mail_server.ehlo()
            mail_server.login("mahia020005@gmail.com", "bvlkzjxeyalgrzua")
            mail_server.sendmail(self.sender, receiver, msg.as_string())
            mail_sent = True
        except Exception as e:
            print("Error occured while sending email", e)
            mail_sent = False
        finally:
            if mail_server:
                mail_server.quit()
        return mail_sent

if __name__ == "__main__":
    sm = SMTPManager()
    sm.send_email("mahia000003@gmail.com", "123455")