from flask import Flask, render_template, request, redirect, url_for, flash, session
from pymongo import MongoClient
from utilities import *
from bson import ObjectId
import os
import datetime
from datetime import datetime  

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['MONGO_URI'] = 'mongodb+srv://imaad:Ertdfgx%400@cluster0.9wdyedm.mongodb.net/'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] =  465 
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'ssebintuimaad@gmail.com'
app.config['MAIL_PASSWORD'] = 'qcrxtdznftzrubfv'
app.config['MAIL_DEFAULT_SENDER'] = 'ssebintuimaad@gmail.com' 
mail = Mail(app)
mongo = MongoClient(app.config['MONGO_URI'])
db = mongo['URA']
User = db['User']
client = db['Client']
VehicleTransfer = db['VehicleTransfer']

@app.route('/register', methods=['GET', 'POST'])
@is_user_logged_in
def register():
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        gender = request.form['gender']
        telephone = request.form['telephone'] 
        if create_user(firstname, lastname, username, email, password, gender, telephone):
            return redirect(url_for('register'))
        else:
            return redirect(url_for('register'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
@is_user_logged_in
def login():
    if request.method == 'POST':
        email_or_username = request.form['email_or_username']
        password = request.form['password']
        if login_user(email_or_username, password):
            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def dashboard():
    userId = session['userId']
    user = User.find_one({'_id': ObjectId(userId)})
    if user:
        username = user['username']
        email = user['email']
        return render_template('dashboard.html', username=username, email=email)
    else:
        flash('User not found!', 'error')
        return redirect(url_for('login'))

@app.route('/reset_password_request', methods=['GET', 'POST'])
@is_user_logged_in
def reset_password_request():
    if request.method == 'POST':
        email = request.form['email']
        success = send_reset_email(email)
        if success:
            flash('An email with instructions to reset your password has been sent.')
            return redirect(url_for('login'))
        else:
            flash('Email address not found.')
    return render_template('reset_password_request.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
@is_user_logged_in
def reset_password(token):
    user = User.find_one({'reset_token': token, 'reset_token_expiration': {'$gt': datetime.datetime.utcnow()}})
    if not user:
        flash('Invalid or expired token.')
        return redirect(url_for('login'))
    if request.method == 'POST':
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password != confirm_password:
            flash('Password and confirm password do not match.')
            return render_template('reset_password.html', token=token)
        User.update_one({'_id': user['_id']}, {'$set': {'password': password}, '$unset': {'reset_token': '', 'reset_token_expiration': ''}})
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', token=token)


@app.route('/add-vehicle-transfer', methods=['GET', 'POST'])
@login_required
def add_vehicle_transfer():
    if request.method == 'POST':
        vehicle_registration_number = request.form['vehicle_registration_number']
        search_code = request.form['search_code']
        notice_number = request.form['notice_number']
        current_owner_name = request.form['current_owner_name']
        new_owner_name = request.form['new_owner_name'] 
        date_of_transfer = request.form['date_of_transfer']      
        user_id = ObjectId(session['userId'])     
        transfer_data = {
            'user_id': user_id,
            'vehicle_registration_number': vehicle_registration_number,
            'search_code': search_code,
            'notice_number': notice_number,
            'current_owner_name': current_owner_name,
            'new_owner_name': new_owner_name,
            'saved_at': datetime.now(),
            'date_of_transfer': date_of_transfer
        }
        VehicleTransfer.insert_one(transfer_data)
        flash('Vehicle transfer record added successfully.', 'success')
        return redirect(url_for('dashboard'))   
    return render_template('add_vehicle_transfer.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
