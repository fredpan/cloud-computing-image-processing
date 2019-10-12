import datetime
import re
import time
import mysql.connector
from flask import render_template, redirect, url_for, request, g, session
from app import webapp
from app.route_sample import go_to_main_page
from app.sql.config.config import db_config
from app import send_email as email_confirmation


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
    return render_template("/login_index.html", title="Welcome")

@webapp.route('/login_submit', methods=['POST'])
def login_submit():
    username = request.form['username']
    password = request.form['password']

    # connect to database
    cnx = get_database()
    cursor = cnx.cursor()
    query = "SELECT COUNT(username) FROM user_info WHERE username = %s and password = %s and active = 1"
    cursor.execute(query, (username, password))
    results = cursor.fetchall()
    numberOfMatchedResults = results[0][0]

    if numberOfMatchedResults == 1:
        session['authenticated'] = True
        session['username'] = username
        session['error'] = None
        return redirect(url_for('sensitive'))

    session['username'] = username
    session['error'] = "<=Error! Incorrect username or password!=>"

    return render_template("/login_index.html", title="Main Page", username = username, error=session['error'])

"""
#############################################################
Sign up Settings
############################################################
"""

@webapp.route('/signup', methods=['GET'])
# Display an empty HTML form that allows users to fill the info and sign up.
def user_signup():
    return render_template("signup_index.html", title="Join Us!")

@webapp.route('/signup/save', methods=['POST'])
# Create a new account and save them in the database.
def sign_up_save():
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

    ts = time.time()
    timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

    query = ''' INSERT INTO user_info (username,password,create_date,active)
                       VALUES (%s,%s, %s,1)
    '''

    cursor.execute(query, (username, password1, timestamp))
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
    if 'authenticated' not in session:
        return redirect(url_for('user_login'))

    if session['authenticated'] == True:
        # connect to database
        cnx = get_database()
        cursor = cnx.cursor()
        query = "SELECT create_date FROM user_info WHERE username = %s"
        cursor.execute(query, (session['username'],))
        results = cursor.fetchall()
        membersince = results[0][0]

        session['membersince'] = membersince

        return render_template("/secured_index.html", username=session['username'], membersince=session['membersince'])
    else:
        return redirect(url_for('user_login'))

@webapp.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return redirect(url_for("sensitive"))

"""
#############################################################
Send Email
############################################################
"""

@webapp.route('/signup/send_email', methods=['POST'])
# Create a new account and save them in the database.
def send_email():
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



