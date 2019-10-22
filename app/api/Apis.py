import datetime
import os
import re
import time
from flask import request
from flask_bcrypt import Bcrypt
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.utils import secure_filename
from app import webapp
from app.AccountManagment import validUsernameChar, get_database
from app.FileUploader import UPLOAD_FOLDER
from app.api.HttpResponse import http_response
from app.opencv import Opencv


@webapp.route('/api/register', methods=['POST'])
def user_register_api():
    '''
    This function takes POST http request with a URL of "/api/register". It firstly reads the user submitted username
    and password. It then connects to the database to check if there is already an existing username in the database.
    The function also checks whether the user provided all the necessary information; whether the format of the
    username and password are correct. If any of the above conditions failed, the function will return user with a
    formatted Json string including the error code and error message. If all the condition check passed, the function
    will create a new entry in the dataset and return a Json string with code 200 indicating request processed
    successfully.
    :return: Json string with status code and information string
    '''

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

    if numberOfExistUser != 0:
        return http_response(409, "Error: User name already exist!")

    if username == "" or password == "":
        return http_response(400, "Error: All fields are required!")

    if re.findall(r'\s+', username) != []:
        return http_response(400, "Error: No space allowed in user name!")

    if (len(username) > 20 or len(username) < 1) or not all(c in validUsernameChar for c in username):
        return http_response(400, "Error: Username violation, username must have length between 1 to 20, only letters and numbers allowed")

    if len(password) > 16 or len(password) < 1:
        return http_response(400, "Error: Password length violation")

    ts = time.time()
    timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

    password = bcrypt.generate_password_hash(password).decode("utf-8")

    query = ''' INSERT INTO user_info (username,password,create_date,active,upload_counter)
                           VALUES (%s,%s, %s,1,0)
        '''

    cursor.execute(query, (username, password, timestamp))
    cnx.commit()

    # Add error catch here for sql

    return http_response(200, "Registration succeed for the user: " + username)

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
webapp.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#after user click the upload button
@webapp.route('/api/upload', methods=['POST'])
def upload_file_api():
    '''
    This function provides users with an api to upload an image together with given username and password.
    The function will first check if the user info is correct and if it's correct, the function will keep a record
    of the image and an OpenCV-processed image in the database, with the proper naming scheme.
   The function can raise exceptions if there are any of the following problems: no file selected; filename too long;
   wrong extension type; file too large.
   If the uploaded is valid then we will connect to the database and create a record. First, we assign systematic names
   to the image and its processed image depending on the user id and their upload counter. Second, we save the image
   to the cloud, process it through OpenCV and then save the processed image to the cloud. Third, we gather all
   information and update our file name table in the database.
   Last we increase the upload counter by 1 and update it.
    :return: Json string with status code and information string
    '''
    bcrypt = Bcrypt(webapp)
    try:
        username = request.form['username']
        password = request.form['password']

        if request.method == 'POST':

            # check if the post request has the file part
            if 'file' not in request.files:
                return http_response(404, "No file upload in the request!")

            try:
                file = request.files['file']
            except RequestEntityTooLarge:
                return http_response(413, "Image too large, file cannot larger than 5mb")

            # if user does not select file, browser also
            # submit an empty part without filename
            if file.filename == '':
                return http_response(404, "No file selected!")
            if len(file.filename) >= 50:
                return http_response(400, "File name too long")
            if file and allowed_file(file.filename):

                #===================================================#
                #======Till this step the file is good to process===#
                # ===================================================#

                #rename the upload img as: userpid_useruploadcounter_imagename.extention
                userFileName = secure_filename(file.filename)  # example: example.jpg

                # connect to database
                cnx = get_database()
                cursor = cnx.cursor()
                query1 = "SELECT password, uid, upload_counter FROM user_info WHERE username = %s and active = 1"
                cursor.execute(query1, (username,))
                results = cursor.fetchall()

                if len(results)!=1:
                    return http_response(400, "Invalid username or password")

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
                    Opencv.imageProcess(UPLOAD_FOLDER, cloudSaveFilename, cloudProcessedFileName)

                    #prepare for values for sql
                    fileName = userFileName
                    processedFileName = "processed_" + userFileName
                    uploadImagePath = UPLOAD_FOLDER + cloudSaveFilename
                    processedImagePath = UPLOAD_FOLDER + cloudProcessedFileName
                    ts = time.time()
                    timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

                    #update file_name table
                    query2 = "INSERT INTO file_info (uid, file_name, upload_image_path, cloud_image_name, processed_image_path, cloud_processed_image_name, create_time) VALUES (%s, %s, %s, %s, %s , %s, %s)"
                    data = (uid,fileName,uploadImagePath,cloudSaveFilename, processedImagePath,cloudProcessedFileName, timeStamp)
                    cursor.execute(query2, data)
                    cnx.commit()

                    #get the newest user upload counter for database
                    query3 = "SELECT upload_counter FROM user_info WHERE username = %s and active = 1"
                    cursor.execute(query3, (username,))
                    results = cursor.fetchall()
                    upload_counter = results[0][0]

                    #update user_table
                    query4 = "UPDATE user_info SET upload_counter = %s WHERE uid = %s"
                    cursor.execute(query4, (upload_counter+1, uid))
                    cnx.commit()

                    print("==>process succeed")
                    # get the image path for both image_before and image_after
                    return http_response(200, "Image Successfully Processed!")

                else:
                    return http_response(400, "Invalid username or password")

            else:
                return http_response(400, "Not a Correct File Type!"+str(file and allowed_file(file.filename))+"|"+file.filename)
        return http_response(123, "Unsupported method!")


    except Exception as ex:
        if '413' in str(ex):
            return http_response(413, "Image too large, file cannot larger than 5mb")
        return http_response(400, str(ex))
