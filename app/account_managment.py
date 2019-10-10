import datetime
import re
import time
import mysql.connector
from flask import render_template, redirect, url_for, request, g, session
from app import webapp
from app.sql.config.config import db_config

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


@webapp.route('/login', methods=['GET'])
# Display an empty HTML form that allows users to fill in info to login
def user_login():
    return render_template("account/login_form.html", title="Login!")

@webapp.route('/login', methods=['GET', 'POST'])
def login():
    return render_template("login_form.html")

@webapp.route('/login_submit', methods=['POST'])
def login_submit():
    # connect to database
    cnx = get_database()
    cursor = cnx.cursor()
    query = "SELECT COUNT(user_name) FROM user_info WHERE user_name = %s and user_key = %s "
    cursor.execute(query, (request.form['username'], request.form['password']))
    results = cursor.fetchall()
    numberOfMatchedResults = results[0][0]

    if numberOfMatchedResults == 1:
        session['authenticated'] = True
        session['username'] = request.form['username']
        session['error'] = False
        return redirect(url_for('sensitive'))

    if 'username' in request.form:
        session['username'] = request.form['username']

    session['error'] = "Error! Incorrect username or password!"

    return render_template("/account/login_form.html", title="Login!", error="Error! Incorrect username or password!")

"""
#############################################################
Sign up Settings
############################################################
"""

@webapp.route('/signup', methods=['GET'])
# Display an empty HTML form that allows users to fill the info and sign up.
def user_signup():
    return render_template("account/sign_up_form.html", title="Join Us!")

@webapp.route('/signup/save', methods=['POST'])
# Create a new student and save them in the database.
def sign_up_save():
    # need to trim the user name
    username = request.form.get('username', "")
    password1 = request.form.get('password1', "")
    password2 = request.form.get('password2', "")
    email = request.form.get('email', "")

    error = False

    # connect to database
    cnx = get_database()
    cursor = cnx.cursor()
    query = "SELECT COUNT(user_name) FROM user_info WHERE user_name = %s "
    cursor.execute(query, (username,))
    results = cursor.fetchall()
    numberOfExistUser = results[0][0]

    if numberOfExistUser != 0:
        error = True
        error_msg = "Error: User name already exist!"

    if username == "" or password1 == "" or password2 == "" or email == "":
        error = True
        error_msg = "Error: All fields are required!"

    if not error and not re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", email):
        error = True
        error_msg = "Error: Not a correct email address!"

    if not (password1 == password2):
        error = True
        error_msg = "Error: Two passwords not matching!"

    if error:
        return render_template("account/sign_up_form.html", title="Join Us!", error_msg=error_msg,
                               username=username, email=email, password1=password1, password2=password2)

    ts = time.time()
    timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

    query = ''' INSERT INTO user_info (user_name,user_key,user_email,user_create_date)
                       VALUES (%s,%s, %s,%s)
    '''

    cursor.execute(query, (username, password1, email, timestamp))
    cnx.commit()

    # Add error catch here for sql

    # Send Email
    send_email.send_email(email, username, password1)

    return render_template("/account/register_succeed.html", title="You are In!", name=username, password=password1)


"""
#############################################################
Secure Index
############################################################
"""
@webapp.route('/secure/index', methods=['GET', 'POST'])
def sensitive():
    if 'authenticated' not in session:
        return redirect(url_for('login'))

    # connect to database
    cnx = get_database()
    cursor = cnx.cursor()
    query = "SELECT user_create_date FROM user_info WHERE user_name = %s "
    cursor.execute(query, (session['username'],))
    results = cursor.fetchall()
    memberSince = results[0][0]

    return render_template("/account/login_succeed.html", name=session['username'], date=memberSince)

@webapp.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return redirect(url_for('sensitive'))







