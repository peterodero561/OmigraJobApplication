from flask import Flask, render_template, redirect, flash, request, url_for, session, jsonify
from flask_cors import CORS
from flask_login import current_user, login_required
from flask_mail import Mail, Message
from flask_mysqldb import MySQL
from flask_sqlalchemy import SQLAlchemy
import os
import MySQLdb.cursors
from models.db import db
from models.job import Job
from models.user import User
import re
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename



# create app
app = Flask(__name__)
app.secret_key = 'Peter 1234'

# configure picture upload
UPLOAD_FOLDER = 'static/images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Configure mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'peterodero561@gmail.com'
app.config['MAIL_PASSWORD'] = os.getenv('Password')
app.config['MAIL_USE_TSL'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

# Configuration for the MySQL database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Peterodero561%40@localhost/omigra'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database with the app context
db.init_app(app)

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
        account = User.query.filter_by(username=username).first()

        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif not username or not password or not email:
            msg = 'Please fill out the form !'
        else:
            # Create a new user instance
            new_user = User(username=username, password=password, email=email)
            db.session.add(new_user)
            db.session.commit()
            msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg = msg)


@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'profile_pic' not in request.files:
        return "No file part"
    file = request.files['profile_pic']
    if file.filename == '':
        return "No selected file"
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Update the user's profile picture path in the database
        current_user.profile_pic = filepath
        db.session.commit()
        
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
