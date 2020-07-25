from werkzeug.security import check_password_hash

class User:
    def __init__(self,email,password,fname,status):
        self.email = email
        self.password = password
        self.fname = fname
        self.status = status
    
    @staticmethod
    def is_authenticated(self):
        return True
    
    @staticmethod
    def is_active(self):
        return True
    
    @staticmethod
    def is_anonymous(self):
        return False

    def get_id(self):
        return self.email

    def check_password(self,password_input):
        return check_password_hash(self.password,password_input)