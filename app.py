from flask import Flask, render_template, redirect, flash, request, url_for, session
from flask_cors import CORS
from flask_login import current_user, login_required
from flask_mail import Mail, Message
from flask_mysqldb import MySQL
import os
import MySQLdb.cursors
from models.user import User
import re
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

# configure for MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Peterodero561@'
app.config['MYSQL_DB'] = 'omigra'

mysql = MySQL(app)

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
    user = User(id=session['id'], username=session['username'])
    return render_template('home.html')

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
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = % s AND password = % s', (username, password, ))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            user = User(id=account['id'], username=account['username'], profile_pic=account.get('profile_pic'))
            msg = 'Logged in successfully !'
            return render_template('home.html', msg = msg, user=user)
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
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = % s', (username, ))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif not username or not password or not email:
            msg = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO accounts VALUES (NULL, % s, % s, % s)', (username, password, email, ))
            mysql.connection.commit()
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




if __name__ == '__main__':
    app.run(debug=True)
