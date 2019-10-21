import datetime
import os
import time

import mysql.connector
from flask import request, redirect, url_for, send_from_directory, render_template, session, g
from werkzeug.utils import secure_filename

from app import webapp
from app.opencv import Opencv
from app.sql.config.DbConfig import db_config


# The function used to establish connection to sql database
def connect_to_database():
    return mysql.connector.connect(user=db_config['user'],password=db_config['password'],host=db_config['host'],database=db_config['database'])

def get_database():
    '''
    Description:
    These two functions allow us to connect to database and get basic information
    :return: connected database object
    '''
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect_to_database()
    return db




#UPLOAD_FOLDER = '/home/ubuntu/ece1779_projects/img/'

#UPLOAD_FOLDER = '/Users/fredpan/Desktop/output/'

#UPLOAD_FOLDER = '/home/yixiao/Desktop/after/'

UPLOAD_FOLDER = '/home/ubuntu/ece1779_projects/img/'


ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
webapp.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    '''
    Description:
    This function checks allowed extension type.
    :param filename: The file name which need to be judged
    :return: True if the file is illegible and False if its not
    '''
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#after user click the upload button
@webapp.route('/upload', methods=['POST'])
def upload_file():
    '''
    Description:

    This function will be called if the user tries to upload an image and this function checks if the upload is valid.
    If so the function will keep a copy of the image and an OpenCV-processed image in the database, with the proper
    naming scheme.
    The function can raise exceptions if there are any of the following problems: no file selected; filename too long;
    wrong extension type; file too large.
    If the uploaded is valid then we will connect to the database and create a record. First, we update the information
    in session from our database. Second, we assign systematic names to the image and its processed image depending on
    the user id and their upload counter. Third, we save the image to the cloud, process it through OpenCV and then
    save the processed image to the cloud. Fourth, we gather all information and update our file name table in the
    database. Last we increase the upload counter by 1 and update it.
    :return: upload_management.html
    '''

    try:
        if request.method == 'POST':
            file = request.files['file']
            # check if the post request has the file part
            if 'file' not in request.files:
                raise Exception("No file upload in the request!")

            # test if file too large:

            # if user does not select file, browser also

            # submit an empty part without filename
            if file.filename == '':
                raise Exception("No file selected!")
            if len(file.filename) >= 50:
                raise Exception("File name too long")

            if file and allowed_file(file.filename):

                #===================================================#
                #======Till this step the file is good to process===#
                # ===================================================#

                # connect to database and create the record
                cnx = get_database()
                cursor = cnx.cursor()

                #update uploadCounter in current session
                query = "SELECT upload_counter FROM user_info WHERE uid = %s"
                cursor.execute(query, (session['uid'],))
                results = cursor.fetchall()
                session["uploadCounter"] = results[0][0]

                #rename the upload img as: userpid_useruploadcounter_imagename.extention
                userFileName = secure_filename(file.filename)  # example: example.jpg
                cloudSaveFilename = str(session["uid"]) + "_" + str(session["uploadCounter"]) + "_" + userFileName  #example: 12_1_example.jpg
                cloudProcessedFileName = "p_" + cloudSaveFilename
                userDownloadFileName = "processed_" + userFileName

                # save uploaded img to cloud drive
                file.save(os.path.join(webapp.config['UPLOAD_FOLDER'], cloudSaveFilename))

                #process the img from cloud drive, it will process the img in (img_path) and save processed img in same path
                Opencv.imageProcess(UPLOAD_FOLDER, cloudSaveFilename, cloudProcessedFileName)

                #prepare for values for sql
                uid = session["uid"]
                fileName = userFileName
                processedFileName = "processed_" + userFileName
                uploadImagePath = UPLOAD_FOLDER + cloudSaveFilename
                processedImagePath = UPLOAD_FOLDER + cloudProcessedFileName
                ts = time.time()
                timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

                #update file_name table
                query = "INSERT INTO file_info (uid, file_name, upload_image_path, cloud_image_name, processed_image_path, cloud_processed_image_name, create_time) VALUES (%s, %s, %s, %s, %s , %s, %s)"
                data = (uid,fileName,uploadImagePath,cloudSaveFilename, processedImagePath,cloudProcessedFileName, timeStamp)
                cursor.execute(query, data)
                cnx.commit()

                #update uploadCounter in current session
                query = "SELECT upload_counter FROM user_info WHERE uid = %s"
                cursor.execute(query, (session['uid'],))
                results = cursor.fetchall()
                session["uploadCounter"] = results[0][0]

                #update user_table
                query = "UPDATE user_info SET upload_counter = %s WHERE uid = %s"
                cursor.execute(query, (session["uploadCounter"]+1, session["uid"]))
                cnx.commit()

                #update uploadCounter in current session
                query = "SELECT upload_counter FROM user_info WHERE uid = %s"
                cursor.execute(query, (session['uid'],))
                results = cursor.fetchall()
                session["uploadCounter"] = results[0][0]

                # get the image path for both image_before and image_after
                info_msg = "Image Successfully Processed!"

                return render_template("upload_management.html", uploadImagePath= "/uploads/" + cloudSaveFilename,
                                       processedImagePath="/uploads/"+cloudProcessedFileName, fileName=fileName,
                                       processedFileName=processedFileName, info_msg=info_msg)

            else:
                raise Exception("Not a Correct File Type!")
    except Exception as ex:
        print("problem is:", str(ex))
        return render_template("upload_management.html", error_msg=str(ex))

@webapp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(webapp.config['UPLOAD_FOLDER'],filename)


@webapp.route('/file_management')
def file_management():
    '''
    This function allows user to check uploaded and processed images when the url'/file_management' is called.
    If the session information is all valid, we will connect to the database and try to get all images with the
    required uid and then show them.
    :return: "file_management.html"
    '''
    if ('authenticated' in session) and ('username' in session):
        #check if the cookie includes username and authenticated flag
        if session['authenticated'] == True:
            #==========prepare the loop for flexable amont of images===========#
            # connect to database and create the record
            cnx = get_database()
            cursor = cnx.cursor()
            query = "SELECT file_name, cloud_image_name, cloud_processed_image_name FROM file_info WHERE uid = %s"
            cursor.execute(query, (session['uid'],))
            results = cursor.fetchall()

            #if there is no uploaded image:
            if len(results) == 0:
                return render_template("file_management.html",fileNumber=0, dictList=[])

            # if there exists uploaded image:
            else:
                # need following args for render html template : dictList, filenumber>0
                # for each dictionary in dictList, 5 elements:
                # modelName: ex. model1
                # cloudSaveFilename: ex. 07_2_example.jpg
                # cloudProcessedFileName ex. p_07_2_example.jpg
                # userFileName: ex. example.jpg
                # processedUserFileName: ex. processed_example.jpg

                dictList = []
                fileNumber = len(results)



                #build the dictList
                for i in range(fileNumber):
                    newdict = dict()
                    newdict["userFileName"] = results[i][0]
                    newdict["cloudSaveFilename"] = results[i][1]
                    newdict["cloudProcessedFileName"] = results[i][2]
                    newdict["processedUserFileName"] = "processed_" + results[i][0]
                    newdict["modalID"] = "modal" + str(i)
                    newdict["buttonID"] = "button" + str(i)
                    newdict["closeID"] = "close" + str(i)

                    dictList.append(newdict)

                return render_template("file_management.html",fileNumber=fileNumber, dictList=dictList)

    else:
        return redirect(url_for('user_login'))