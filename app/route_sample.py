from flask import Flask
from flask import render_template
from app import webapp


@webapp.route('/index.html')
def hello_world():
    return render_template("index.html")


@webapp.route('/')
def hello_world56():
    return render_template("index.html")


@webapp.route('/upload_management.html')
def hello_world1():
    return render_template("upload_management.html")


@webapp.route('/file_management.html')
def hello_world2():
    return render_template("file_management.html")