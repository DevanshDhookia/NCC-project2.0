import hashlib

class LoginValidator():
    
    def is_user_logged_in(self, request):
        if request.session.get('token'):
            return True
        return False
    
    def password_encrypter(self, password):
        hashobject = hashlib.sha256(usedforsecurity=True)
        hashobject.update(password.encode())
        hash_password = hashobject.hexdigest()
        return hash_password
    
    