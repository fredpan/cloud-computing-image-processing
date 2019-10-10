from flask import Flask
from flask import render_template,session,redirect,url_for
from app import webapp

@webapp.route('/')
def go_to_main_page():
    if ('authenticated' in session) and ('username' in session):
        #check if the cookie includes username and authenticated flag
        if session['authenticated'] == True:
            return render_template("secured_index.html", title="MainPage",username=session['username'])
        else:
            if 'username' in session:
                session.pop('username')
            if 'authenticated' in session:
                session.pop('authenticated')
            return redirect(url_for('user_login'))
    else:
        if 'username' in session:
            session.pop('username')
        if 'authenticated' in session:
            session.pop('authenticated')
        return redirect(url_for('user_login'))


@webapp.route('/upload_management.html')
def upload_management():
    return render_template("upload_management.html")

@webapp.route('/file_management.html')
def file_management():
    return render_template("file_management.html")