from flask import Flask
from flask import render_template

app = Flask(__name__)


@app.route('/index.html')
def hello_world():
    return render_template("index.html")


@app.route('/')
def hello_world56():
    return render_template("index.html")


@app.route('/generic.html')
def hello_world1():
    return render_template("generic.html")

@app.route('/gallery.html')
def hello_world2():
    return render_template("gallery.html")


if __name__ == '__main__':
    app.run()
