from flask import render_template, session, redirect, url_for
from app import webapp
from flask import render_template, session, redirect, url_for

from app import webapp


@webapp.route('/')
def go_to_main_page():
    '''
    Description:

    This function runs when homepage url'/' is called, and redirect the user to login page or secured page.
    It checks if the authenticated and username information in session. If they are both in the session and the
    authenticated is true, the user will be directed to the secured page. If anything doesn't satisfy the requirements
    above, the user will then be directed to login page and authenticated and username information in session will be
    cleared.

    :return: login_index.html or secured_index.html
    '''
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
    '''
    Description:

    This function runs when upload_management page url'/upload_management' is called, and redirect user to
    upload_management page only if all session condition requirements (as mentioned in go_to_main_page) are satisfied.
    Otherwise the user will then be directed to login page and authenticated and username information in session will
    be cleared.

    :return: upload_management.html or login_index.html
    '''
    if ('authenticated' in session) and ('username' in session):
        #check if the cookie includes username and authenticated flag
        if session['authenticated'] == True:
            return render_template("upload_management.html")
    else:
        return redirect(url_for('user_login'))


