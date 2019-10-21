import datetime
import re
import time
import mysql.connector
from flask import render_template, redirect, url_for, request, g, session
from flask_bcrypt import Bcrypt
from app import EmailSender as email_confirmation
from app import webapp
from app.sql.config.DbConfig import db_config

validUsernameChar = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

# The function used to establish connection to sql database
def connect_to_database():
    return mysql.connector.connect(user=db_config['user'],password=db_config['password'],host=db_config['host'],database=db_config['database'])

def get_database():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect_to_database()
    return db

"""
#############################################################
Login Settings
############################################################
"""

@webapp.route('/login', methods=['GET', 'POST'])
def user_login():
    '''
    This function takes GET/POST http request with URL of "/login"
    It returns the user with an html website of the login page
    :return: the rendered "login_index.html"
    '''
    return render_template("/login_index.html", title="Welcome")

@webapp.route('/login_submit', methods=['POST'])
def login_submit():
    '''
    This function takes POST http request with URL of "/login_submit". It firstly reads the user submitted username,
    password and the check statue of "remember me" option based on whether the user checked "remember me" the function
    adjust the session expiry time by adjusting the value of webapp.permanent_session_lifetime. The function then
    connects to the database and reads the search results based on user inputs. If no search results find based on
    the user provided username, the function will return the user with "login_index.html" with error message; if the
    user input password doesn't match the database password after bcrypt,the function will return the user with
    login_index.html" with error message; If it passed all the condition, the function will redirect to URL"/secure/index"
    :return: /login_index.html or /secure/index

    '''
    session.permanent = True
    bcrypt = Bcrypt(webapp)
    username = request.form['username']
    password = request.form['password']
    remember = request.form.get('remember')
    print(remember)
    rememberMe = False
    #if remember!=None and remember=="on":
    if remember:
        rememberMe = True
    else:
        session.clear()
        webapp.permanent_session_lifetime = datetime.timedelta(milliseconds=0)
    #password = bcrypt.generate_password_hash(password).decode("utf-8")
    #bcrypt.check_password_hash
    # connect to database
    cnx = get_database()
    cursor = cnx.cursor()
    query = "SELECT password FROM user_info WHERE username = %s and active = 1"
    cursor.execute(query, (username,))
    results = cursor.fetchall()
    if len(results)==1:
        hashed_pwd = results[0][0]
        if bcrypt.check_password_hash(hashed_pwd,password):
            session['authenticated'] = True
            session['username'] = username
            session['error'] = None
            if rememberMe:
                webapp.permanent_session_lifetime = datetime.timedelta(weeks=1)
            return redirect(url_for('sensitive'))

    session['username'] = username
    session['error'] = "<=Error! Incorrect username or password!=>"

    return render_template("/login_index.html", title="Main Page", username = username, error=session['error'])

"""
#############################################################
Sign up Settings
############################################################
"""

# Display an empty HTML form that allows users to fill the info and sign up.
@webapp.route('/signup', methods=['GET'])
def user_signup():
    '''
    This function takes GET http request with URL of "/signup"
    It returns the user with an html website of the signup page
    :return: the rendered "signup_index.html"
    '''
    return render_template("signup_index.html", title="Join Us!")

# Create a new account and save them in the database.
@webapp.route('/signup/save', methods=['POST'])
def sign_up_save():
    '''
    This function takes POST http request with a URL of "/signup/save". It firstly reads the user submitted username,
    password1 and password2. It then connects to the database to check if there is already an existing username in the
    database. The function also checks whether the user provided all the necessary information; whether the format of
    the username and password are correct and whether the two passwords match. If any of the above condition failed,
    the function will return user with "signup_index.html" with error message. If not, the function will insert the
    user provided information to the database and return "signup_succeed_index.html" page to user indicating the user
    has successfully created a new account.
    :return: "signup_index.html"  or "signup_succeed_index.html"
    '''

    bcrypt = Bcrypt(webapp)
    # need to trim the user name
    username = request.form.get('username', "")
    password1 = request.form.get('password1', "")
    password2 = request.form.get('password2', "")

    # connect to database
    cnx = get_database()
    cursor = cnx.cursor()
    query = "SELECT COUNT(username) FROM user_info WHERE username = %s "
    cursor.execute(query, (username,))
    results = cursor.fetchall()
    numberOfExistUser = results[0][0]


    if username == "" or password1 == "" or password2 == "":
        error_msg = "Error: All fields are required!"
        return render_template("signup_index.html", title="Sign Up", error_msg=error_msg,
                               username=username, password1=password1, password2=password2)

    if re.findall(r'\s+',username)!=[]:
        error_msg = "Error: No space allowed in user name!"
        return render_template("signup_index.html", title="Sign Up", error_msg=error_msg,
                               username=username, password1=password1, password2=password2)

    if numberOfExistUser != 0:
        error_msg = "Error: User name already exist!"
        return render_template("signup_index.html", title="Sign Up", error_msg=error_msg,
                               username=username, password1=password1, password2=password2)

    if not (password1 == password2):
        error_msg = "Error: Two passwords not matching!"
        return render_template("signup_index.html", title="Sign Up", error_msg=error_msg,
                               username=username, password1=password1, password2=password2)

    if (len(username) > 20 or len(username) < 1) or not all(c in validUsernameChar for c in username):
        print(len(username))
        error_msg = "Error: Username violation, username must have length between 1 to 20, only letters and numbers allowed"
        return render_template("signup_index.html", title="Sign Up", error_msg=error_msg,
                               username=username, password1=password1, password2=password2)

    if len(password1)>16 or len(password1)<1:
        error_msg = "Error: Password length violation"
        return render_template("signup_index.html", title="Sign Up", error_msg=error_msg,
                               username=username, password1=password1, password2=password2)


    ts = time.time()
    timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

    password = bcrypt.generate_password_hash(password1).decode("utf-8")

    query = ''' INSERT INTO user_info (username,password,create_date,active,upload_counter)
                       VALUES (%s,%s, %s,1,0)
    '''

    cursor.execute(query, (username, password, timestamp))
    cnx.commit()

    # Add error catch here for sql

    return render_template("signup_succeed_index.html", title="Sign Up Succeed", username=username, password=password1)


"""
#############################################################
Secure Index
############################################################
"""
@webapp.route('/secure/index', methods=['GET', 'POST'])
def sensitive():
    '''
    This function takes GET/POST http request with URL of "/secure/index". The function firstly check if the user
    session has key of “authenticated” and value of True which indicating the user has passed the security check.
    If not, the user will be redirected back  to ‘/user_login’. If the user session contains “authenticated” and
    has a value of True, the function will perform a database search based on the “username” in the client’s
    session and store the user’s uid, upload_counter and create_date into the session and return the page
    of "/secured_index.html".
    :return: "/secure/index" or  "/secured_index.html"
    '''

    if 'authenticated' not in session:
        return redirect(url_for('user_login'))

    #==========Read user Info and sign in =========#
    if session['authenticated'] == True:
        # connect to database
        cnx = get_database()
        cursor = cnx.cursor()
        query = "SELECT uid,  upload_counter , create_date FROM user_info WHERE username = %s and active = 1"
        cursor.execute(query, (session['username'],))
        results = cursor.fetchall()
        uid = results[0][0]
        uploadCounter = results[0][1]
        memberSince = results[0][2]

        session['uid'] = uid
        session['uploadCounter'] = uploadCounter
        session['membersince'] = memberSince

        return render_template("/secured_index.html", username=session['username'], membersince=session['membersince'])
    else:
        return redirect(url_for('user_login'))

@webapp.route('/logout', methods=['GET', 'POST'])
def logout():
    '''
    This function takes GET/POST http request with URL of “/logout”. The function clear all the contents in the
    current user’s session and terminate the user’s session’s lifetime. The function then redirect the user to
    the main page.
    :return: /secure/index
    '''
    session.clear()
    webapp.permanent_session_lifetime = datetime.timedelta(milliseconds=0)
    return redirect(url_for("sensitive"))

"""
#############################################################
Send Email
############################################################
"""

# Create a new account and save them in the database.
@webapp.route('/signup/send_email', methods=['POST'])
def send_email():
    '''
    This function takes POST http request with URL of “/signup/send_email”. The function read the user email,
    username and password and  check if the user email is in correct form with Regex, if the email address is correct,
    it will call “send_email” function in “EmailSender” class which can send an email to the user with registered
    username and password and redirect the user back to “signup_succeed_index.html” with success message. If the user
    provided email address is not a correct form, the function will redirect back to “signup_succeed_index.html” with
    error message.
    :return: “signup_succeed_index.html”

    '''

    # need to trim the user name
    email = request.form.get('email', "")
    username = request.form.get('username', "")
    password = request.form.get('password', "")

    if not re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", email):
        error_msg = "Error: Not a correct email address!"
        return render_template("signup_succeed_index.html", title="Sign Up Succeed", username=username, password=password, error_msg=error_msg)

    # send email
    email_confirmation.send_email(email,username,password)
    success_msg = "=================Email Sent!==================="
    return render_template("signup_succeed_index.html", title="Sign Up Succeed", username=username, password=password, success_msg = success_msg)




