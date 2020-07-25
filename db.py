from pymongo import MongoClient
from werkzeug.security import generate_password_hash
from user import User

client = MongoClient("mongodb+srv://test:test@blocktrade-mkmqt.mongodb.net/test?retryWrites=true&w=majority")

login_db = client.get_database("LoginDB")
users_collection = login_db.get_collection("users")

def save_user(email,password,fname,lname,ptype):
    password_hash = generate_password_hash(password)
    users_collection.insert_one({'_id':email,'password':password_hash,'status':False,'fname':fname,'lname':lname,'prod_type':ptype})

def get_user(email):
    user_data = users_collection.find_one({'_id': email})
    return User(user_data['_id'],user_data['password'],user_data['fname'],user_data['status']) if user_data else None

def join_user(tradeid,pas):
    user_d = users_collection.find_one({tradeid: pas})
    if user_d:
        return True
    else:
        return False

def update_user(email,i,pas):
    users_collection.update_one({"_id": email}, {"$set": {i: pas}})