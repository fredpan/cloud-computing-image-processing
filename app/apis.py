import json
import os
import re
import time
import datetime
from flask import render_template, request, session, send_from_directory, url_for
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename, redirect

from app import webapp
from app.account_managment import validUsernameChar, get_database
from app.file_uploader import UPLOAD_FOLDER
from app.opencv import opencv


@webapp.route('/api/register', methods=['POST'])
def user_login123():
    bcrypt = Bcrypt(webapp)
    # need to trim the user name
    username = request.form.get('username', "")
    password = request.form.get('password', "")

    # connect to database
    cnx = get_database()
    cursor = cnx.cursor()
    query = "SELECT COUNT(username) FROM user_info WHERE username = %s "
    cursor.execute(query, (username,))
    results = cursor.fetchall()
    numberOfExistUser = results[0][0]

    if username == "" or password == "":
        error_msg = {401:"Error: All fields are required!"}
        #return "Registration failed: " + error_msg
        return json.dump(error_msg)

    if re.findall(r'\s+', username) != []:
        error_msg = "Error: No space allowed in user name!"
        return "Registration failed: " + error_msg

    if numberOfExistUser != 0:
        error_msg = "Error: User name already exist!"
        return "Registration failed: " + error_msg

    if (len(username) > 20 or len(username) < 1) or not all(c in validUsernameChar for c in username):
        print(len(username))
        error_msg = "Error: Username violation, username must have length between 1 to 20, only letters and numbers allowed"
        return "Registration failed: " + error_msg

    if len(password) > 16 or len(password) < 1:
        error_msg = "Error: Password length violation"
        return "Registration failed: " + error_msg

    ts = time.time()
    timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

    password = bcrypt.generate_password_hash(password).decode("utf-8")

    query = ''' INSERT INTO user_info (username,password,create_date,active,upload_counter)
                           VALUES (%s,%s, %s,1,0)
        '''

    cursor.execute(query, (username, password, timestamp))
    cnx.commit()

    # Add error catch here for sql

    return "Succeed"

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
webapp.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#after user click the upload button
@webapp.route('/api/upload', methods=['POST'])
def upload_file123():
    bcrypt = Bcrypt(webapp)
    try:

        username = request.form['username']
        password = request.form['password']

        if request.method == 'POST':
            # check if the post request has the file part
            if 'file' not in request.files:
                print(request)
                raise Exception("No file upload in the request!")
            file = request.files['file']
            # if user does not select file, browser also
            # submit an empty part without filename
            if file.filename == '':
                raise Exception("No file selected!")
            if len(file.filename) >= 20:
                raise Exception("File name too long")

            if file and allowed_file(file.filename):

                #===================================================#
                #======Till this step the file is good to process===#
                # ===================================================#

                #rename the upload img as: userpid_useruploadcounter_imagename.extention
                userFileName = secure_filename(file.filename)  # example: example.jpg

                # connect to database
                cnx = get_database()
                cursor = cnx.cursor()
                query = "SELECT password, uid, upload_counter FROM user_info WHERE username = %s and active = 1"
                cursor.execute(query, (username,))
                results = cursor.fetchall()
                if len(results)!=1:
                    raise Exception("Invalid username")
                correctPwd = bcrypt.check_password_hash(results[0][0], password)
                if correctPwd:
                    uid = results[0][1]
                    upload_counter = results[0][2]

                    cloudSaveFilename = str(uid) + "_" + str(upload_counter) + "_" + userFileName  #example: 12_1_example.jpg
                    cloudProcessedFileName = "p_" + cloudSaveFilename
                    userDownloadFileName = "processed_" + userFileName

                    # save uploaded img to cloud drive
                    file.save(os.path.join(webapp.config['UPLOAD_FOLDER'], cloudSaveFilename))

                    #process the img from cloud drive, it will process the img in (img_path) and save processed img in same path
                    opencv.imageProcess(UPLOAD_FOLDER,cloudSaveFilename,cloudProcessedFileName)

                    #prepare for values for sql
                    fileName = userFileName
                    processedFileName = "processed_" + userFileName
                    uploadImagePath = UPLOAD_FOLDER + cloudSaveFilename
                    processedImagePath = UPLOAD_FOLDER + cloudProcessedFileName
                    ts = time.time()
                    timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

                    # connect to database and create the record
                    cnx = get_database()
                    cursor = cnx.cursor()
                    #update file_name table
                    query = "INSERT INTO file_info (uid, file_name, upload_image_path, cloud_image_name, processed_image_path, cloud_processed_image_name, create_time) VALUES (%s, %s, %s, %s, %s , %s, %s)"
                    data = (uid,fileName,uploadImagePath,cloudSaveFilename, processedImagePath,cloudProcessedFileName, timeStamp)
                    cursor.execute(query, data)
                    cnx.commit()

                    #update user_table
                    query = "UPDATE user_info SET upload_counter = %s WHERE uid = %s"
                    cursor.execute(query, (upload_counter+1, uid))
                    cnx.commit()

                    #update uploadCounter in current session
                    query = "SELECT upload_counter FROM user_info WHERE uid = %s"
                    cursor.execute(query, (uid,))
                    results = cursor.fetchall()

                    # get the image path for both image_before and image_after
                    info_msg = [{"Success":"Image Successfully Processed!"}]

                    return json.dumps(info_msg)

            else:
                raise Exception("Not a Correct File Type!")

    except Exception as ex:
        if '413' in str(ex):
            return "Image too large, file cannot larger than 10mb"
        return str(ex)
