from datetime import datetime
import re,secrets
from pymongo import MongoClient
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash
from flask import Flask ,flash,session 
from functools import wraps
from flask import session, redirect, url_for, flash
import datetime,os

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb+srv://imaad:Ertdfgx%400@cluster0.9wdyedm.mongodb.net/'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] =  465 
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'ssebintuimaad@gmail.com'
app.config['MAIL_PASSWORD'] = 'qcrxtdznftzrubfv'
app.config['MAIL_DEFAULT_SENDER'] = 'ssebintuimaad@gmail.com' 
mail = Mail(app)
mongo = MongoClient(app.config['MONGO_URI'])
app.secret_key = os.urandom(24)
db = mongo['URA']
User = db['User']

def create_user(firstname, lastname, username, email, password, gender, telephone):
    # Check if any required field is empty
    if not (firstname and lastname and username and email and password and gender and telephone):
        flash('All fields are required!', 'error')
        return False   
    existing_user = User.find_one({'$or': [{'username': username}, {'email': email}]})
    if existing_user:
        flash('Username or email already exists!', 'error')
        return False  
    existing_telephone = User.find_one({'telephone': telephone})
    if existing_telephone:
        flash('Telephone number already exists!', 'error')
        return False
    current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    new_user = {
        'firstname': firstname,
        'lastname': lastname,
        'username': username,
        'email': email,
        'password': password,
        'gender': gender,
        'telephone': telephone,
        'created_at': current_date
    }
    User.insert_one(new_user)
    flash('Registration successful!', 'success')
    return True

def login_user(email_or_username, password):
    user = User.find_one({'$or': [{'email': email_or_username}, {'username': email_or_username}], 'password': password})
    if user:
        session['userId'] = str(user['_id'])
        flash('Login successful!', 'success')
        return True
    else:
        flash('Invalid email/username or password!', 'error')
        return False

def login_required(route):
    @wraps(route)
    def wrapper(*args, **kwargs):
        if 'userId' in session:
            return route(*args, **kwargs)
        else:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
    return wrapper

def is_user_logged_in(route):
    @wraps(route)
    def wrapper(*args, **kwargs):
        if 'userId' in session:
            return redirect(url_for('dashboard'))
        return route(*args, **kwargs)
    return wrapper

def send_reset_Email(email, token):
    reset_link = url_for('reset_password', token=token, _external=True)
    msg = Message('Password Reset Request', recipients=[email])
    msg.body = f'To reset your password, visit the following link:\n{reset_link}'
    mail.send(msg)

def send_reset_email(email):
    user = User.find_one({'email': email})
    if user:
        token = secrets.token_urlsafe(16)
        update_reset_token(user['_id'], token)
        send_reset_Email(email, token)
        return True
    else:
        return False

def update_reset_token(user_id, token):
    expiration_time = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    User.update_one({'_id': user_id}, {'$set': {'reset_token': token, 'reset_token_expiration': expiration_time}})
