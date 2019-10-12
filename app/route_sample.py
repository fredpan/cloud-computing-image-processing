from flask import Flask
from flask import render_template,session,redirect,url_for
from app import webapp

@webapp.route('/')
def go_to_main_page():
    #Check if illigiable to goto secured index
    if ('authenticated' in session) and ('username' in session):
        #check if the cookie includes username and authenticated flag
        if session['authenticated'] == True:
            return render_template("secured_index.html", title="MainPage",username=session['username'],membersince=session["membersince"])
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


@webapp.route('/upload_management')
def upload_management():
    if ('authenticated' in session) and ('username' in session):
        #check if the cookie includes username and authenticated flag
        if session['authenticated'] == True:
            return render_template("upload_management.html")
    else:
        return redirect(url_for('user_login'))


@webapp.route('/file_management')
def file_management():
    if ('authenticated' in session) and ('username' in session):
        #check if the cookie includes username and authenticated flag
        if session['authenticated'] == True:
            return render_template("file_management.html")
    else:
        return redirect(url_for('user_login'))