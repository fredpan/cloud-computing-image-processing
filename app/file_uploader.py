import os
from app import webapp
from flask import Flask, flash, request, redirect, url_for, send_from_directory,render_template,session
from werkzeug.utils import secure_filename
from app.opencv import opencv
from app.sql.config.config import db_config

# The function used to establish connection to sql database
def connect_to_database():
    return mysql.connector.connect(user=db_config['user'],password=db_config['password'],host=db_config['host'],database=db_config['database'])

def get_database():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect_to_database()
    return db




#UPLOAD_FOLDER = '/home/ubuntu/ece1779_projects/img/'
UPLOAD_FOLDER = '/home/yixiao/Desktop/img_database'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
webapp.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#after user click the upload button
@webapp.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):

            #example: 01.jpg
            filename = secure_filename(file.filename)

            #generate database name:
            sql_filename = session["username"] + filename

            #check if the filename is already in the database
            # connect to database
            cnx = get_database()
            cursor = cnx.cursor()
            query = "SELECT COUNT(username) FROM user_info WHERE username = %s and password = %s and active = 1"
            cursor.execute(query, (username, password))
            results = cursor.fetchall()
            numberOfMatchedResults = results[0][0]

            #===================================================#
            #======Till this step the file is good to process===#
            # ===================================================#
            try:
                # save uploaded img
                file.save(os.path.join(webapp.config['UPLOAD_FOLDER'], filename))
                img_path = UPLOAD_FOLDER + filename
                #process the img from local
                opencv.imageProcess(img_path)
            except:
                print("error")

        #get the image path for both image_before and image_after
        info_msg = "Image Successfully Processed!"
        image_before = filename
        image_after = filename

    return render_template("secured_index.html", image_before=image_before,image_after=image_after,info_msg=info_msg)


@webapp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(webapp.config['UPLOAD_FOLDER'],filename)