import os
from app import webapp
from flask import Flask, flash, request, redirect, url_for, send_from_directory,render_template,session,g
from werkzeug.utils import secure_filename
from app.opencv import opencv
import mysql.connector
from app.sql.config.config import db_config
import time
import datetime

# The function used to establish connection to sql database
def connect_to_database():
    return mysql.connector.connect(user=db_config['user'],password=db_config['password'],host=db_config['host'],database=db_config['database'])

def get_database():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect_to_database()
    return db




UPLOAD_FOLDER = '/home/ubuntu/ece1779_projects/img/'

#UPLOAD_FOLDER = '/home/yixiao/Desktop/img_database/'


ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
webapp.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#after user click the upload button
@webapp.route('/upload', methods=['POST'])
def upload_file():

    try:

        if request.method == 'POST':
            # check if the post request has the file part
            if 'file' not in request.files:
                raise Exception("No file upload in the request!")
            file = request.files['file']
            # if user does not select file, browser also
            # submit an empty part without filename
            if file.filename == '':
                raise Exception("No file selected!")
            if file and allowed_file(file.filename):

                #===================================================#
                #======Till this step the file is good to process===#
                # ===================================================#

                #rename the upload img as: userpid_useruploadcounter_imagename.extention
                userFileName = secure_filename(file.filename)  # example: example.jpg
                cloudSaveFilename = str(session["uid"]) + "_" + str(session["uploadCounter"]) + "_" + userFileName  #example: 12_1_example.jpg
                cloudProcessedFileName = "p_" + cloudSaveFilename
                userDownloadFileName = "processed_" + userFileName

                # save uploaded img to cloud drive
                file.save(os.path.join(webapp.config['UPLOAD_FOLDER'], cloudSaveFilename))

                #process the img from cloud drive, it will process the img in (img_path) and save processed img in same path
                opencv.imageProcess(UPLOAD_FOLDER,cloudSaveFilename,cloudProcessedFileName)

                #prepare for values for sql
                uid = session["uid"]
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
        print(ex)
        return render_template("upload_management.html", error_msg=ex)

@webapp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(webapp.config['UPLOAD_FOLDER'],filename)


@webapp.route('/file_management')
def file_management():
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