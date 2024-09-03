from flask import Flask, render_template, redirect, flash, request, url_for, session, jsonify
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from flask_migrate import Migrate
from flask_mysqldb import MySQL
from flask_sqlalchemy import SQLAlchemy
import os
import MySQLdb.cursors
from models.db import db
from models.job import Job
from models.user import User
import re
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename



# create app
app = Flask(__name__)
app.secret_key = 'Peter 1234'

# configure picture upload
UPLOAD_FOLDER = 'static/images/profile_pics'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Configure mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'peterodero561@gmail.com'
app.config['MAIL_PASSWORD'] = os.getenv('Password')
app.config['MAIL_USE_TSL'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Configuration for the MySQL database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Peterodero561%40@localhost/omigra'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db) # Initialize Flask-Migrate


# Initialize the database with the app context
with app.app_context():
    db.create_all()  # Create tables if they don't exist


@app.route('/apply', methods=['POST', 'GET'], strict_slashes=False)
def apply():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        message = request.form['message']
        resume = request.files['resume']
        cover_letter = request.files.get('coverLetter')

        # Email
        if resume:
            msg = Message(subject=f'New Job Application from {name}',
                    sender='peterodero561@gmail.com',
                    recipients=['peterodero561@gmail.com'])
            msg.body = f"""
            Name: {name}
            Email: {email}
            Phone: {phone}
            Message: {message}
            """
            msg.attach(resume.filename, resume.content_type, resume.read())
            if cover_letter:
                msg.attach(cover_letter.filename, cover_letter.content_type, cover_letter.read())

            try:
                mail.send(msg)
                flash('Application submitted successfully!', 'success')
            except Exception as e:
                flash(f'Flaied to send application: {str(e)}', 'danger')

            return redirect('/home')
    return render_template('apply.html')


@app.route('/home', strict_slashes=False)
def home():
    jobs = Job.query.all()
    print(f"Number of jobs fetched: {len(jobs)}")

    # Assumming there's a user logged in
    user = None
    if 'id' in session:
         user = User.query.get(session['id'])

    if user:
        print(f"User logged in: {user.username}")
    else:
        print("No user logged in")

    return render_template('home.html', jobs=jobs, user=user)

@app.route('/about', strict_slashes=False)
def about():
    return render_template('about.html')

@app.route('/contact', strict_slashes=False)
def contact():
    return render_template('contact.html')

@app.route('/applyHome', strict_slashes=False)
def applyHome():
    return render_template('apply.html')



@app.route('/', strict_slashes=False)
@app.route('/login', strict_slashes=False, methods =['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        
         # Query the user using SQLAlchemy
        account = User.query.filter_by(username=username).first()

        if account and account.check_password(password):
            login_user(account)
            session['loggedin'] = True
            session['id'] = account.id
            session['username'] = account.username
            session['email'] = account.email
            session['password'] = account.password
            msg = 'Logged in successfully !'
            
            #get all jobs from databse to be displayed
            jobs = Job.query.all()
            return render_template('home.html', msg = msg, user=account, jobs=jobs)
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg = msg)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/register', strict_slashes=False, methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

         # Check if account exists using SQLAlchemy
         # Check if username or email already exists
        existing_user = User.query.filter_by(username=username).first()
        existing_email = User.query.filter_by(email=email).first()

        if existing_user:
            msg = 'Username already exists !'
        if existing_email:
            msg = 'Email already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif not username or not password or not email:
            msg = 'Please fill out the form !'
        else:
            try:
                # Hash the password before storing it
                hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
                # Create a new user instance
                new_user = User(username=username, password=hashed_password, email=email)
                db.session.add(new_user)
                db.session.commit()
                msg = 'You have successfully registered!'
            except IntegrityError:
                db.session.rollback()
                msg = 'An error occurred during registration. Please try again.'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg = msg)


@app.route('/update_information', methods=['POST'])
@login_required
def update_information():
    user = User.query.get(current_user.id)

    if user:
        # update username, email, phone number
        user.username = request.form.get('username')
        user.email = request.form.get('email')
        user.phone_no = request.form.get('phone')
        
        # Update profile picture
        if 'profile-pic' in request.files:
            profile_pic = request.files['profile-pic']
            if profile_pic.filename != '':
                filename = secure_filename(profile_pic.filename)
                profile_pic_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                profile_pic.save(profile_pic_path)
                user.profile_pic = os.path.join('images/profile_pics', filename)
        
        # Update password
        if request.form.get('password') and request.form.get('confirm-password'):
            if request.form.get('password') == request.form.get('confirm-password'):
                user.password = generate_password_hash(request.form.get('password'))
            else:
                flash("Passwords do not match.")
                return redirect(url_for('profile'))
        
        db.session.commit()
        flash("Your information has been updated successfully.")
        return redirect(url_for('home'))
    
    flash("User not found.")
    return redirect(url_for('profile'))
    

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@app.route('/add-job', methods=['POST'])
def add_job():
    job_title = request.form['title']
    job_description = request.form['description']
    
    new_job = Job(title=job_title, description=job_description)
    db.session.add(new_job)
    db.session.commit()
    
    return redirect('/home')

@app.route('/edit-job/<int:id>', methods=['PUT'])
def edit_job(id):
    job_to_edit = Job.query.get_or_404(id)
    
    job_title = request.form['title']
    job_description = request.form['description']
    
    job_to_edit.title = job_title
    job_to_edit.description = job_description
    
    db.session.commit()
    
    return redirect('/home')


@app.route('/delete-job/<int:id>', methods=['POST'])
def delete_job_redirect(id):
    job_to_delete = Job.query.get_or_404(id)
    db.session.delete(job_to_delete)
    db.session.commit()
    
    return redirect('/home')


# API Endpoints

# API for jobs endpoints
@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    '''Gets all jobs posted in the website'''
    jobs = Job.query.all()
    return jsonify([job.to_dict() for job in jobs])

@app.route('/api/jobs/<int:id>', methods=['GET'])
def get_job(id):
    '''Gets a specific job given an id'''
    job = Job.query.get_or_404(id)
    return jsonify(job.to_dict())


@app.route('/api/jobs', methods=['POST'])
def create_job():
    '''Creates a specific job'''
    data = request.json
    new_job = Job(title=data['title'], description=data['description'])
    db.session.add(new_job)
    db.session.commit()
    return jsonify(new_job.to_dict()), 201


@app.route('/api/jobs/<int:id>', methods=['PUT'])
def update_job(id):
    '''Updates a job with a specific id'''
    job = Job.query.get_or_404(id)
    data = request.json
    job.title = data['title']
    job.description = data['description']
    db.session.commit()
    return jsonify(job.to_dict())


@app.route('/api/jobs/<int:id>', methods=['DELETE'])
def delete_job_api(id):
    job = Job.query.get_or_404(id)
    db.session.delete(job)
    db.session.commit()
    return jsonify({'message': 'Job deleted'}), 204


# API for user endpoints
@app.route('/api/users', methods=['GET'])
def get_users():
    '''Get users registered to the website'''
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@app.route('/api/users/<int:id>', methods=['GET'])
def get_user(id):
    '''Gets a specifi user of the website'''
    user = User.query.get_or_404(id)
    return jsonify(user.to_dict())

@app.route('/api/users', methods=['POST'])
def create_user():
    '''Creates a new user to the website'''
    data = request.json
    new_user = User(username='username', email=data['email'], password=generate_password_hash(data['password']))
    db.session.add(new_user)
    db.session.commit()
    return jsonify(new_user.to_dict()), 201

@app.route('/api/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    '''Deletes a user by id'''
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted'}), 204

@app.route('/api/users/<int:id>', methods=['PUT'])
def update_user(id):
    user = User.query.get_or_404(id)
    data = request.json
    user.username = data['username']
    user.email = data['email']
    if 'password' in data:
        user.password = generate_password_hash(data['password'])

    db.session.commit()
    return jsonify(user.to_dict())





if __name__ == '__main__':
    app.run(debug=True)
