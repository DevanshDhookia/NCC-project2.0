from django.conf import settings
import jwt

class JwtUtility():
    def get_jwt_token(self, details):
        encoded_ticket = jwt.encode(details, settings.JWT_SECRET, algorithm="HS256")
        return encoded_ticket

    def get_jwt_data(self, ticket):
        decoded_ticket = jwt.decode(ticket, settings.JWT_SECRET, algorithms=["HS256"])
        return decoded_ticket
