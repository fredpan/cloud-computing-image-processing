from flask import Flask
from flask import render_template

app = Flask(__name__)


@app.route('/index.html')
def hello_world():
    return render_template("index.html")


@app.route('/')
def hello_world56():
    return render_template("index.html")


@app.route('/upload_management.html')
def hello_world1():
    return render_template("upload_management.html")

@app.route('/file_management.html')
def hello_world2():
    return render_template("file_management.html")


if __name__ == '__main__':
    app.run()
