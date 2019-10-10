from flask import Flask
from flask import render_template
from app import webapp

@webapp.route('/')
def go_to_main_page():
    return render_template("index.html")


@webapp.route('/upload_management.html')
def upload_management():
    return render_template("upload_management.html")


@webapp.route('/file_management.html')
def file_management():
    return render_template("file_management.html")