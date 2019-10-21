from app import webapp

'''
This file is the main program which has to be run to start the website service. The program imports the “app” class 
in the same directly which includes all the website framework and resources of our website. The program start the 
webserver with host set to 0.0.0.0 which mean the server listen to all the IP address.
'''
webapp.run(host='0.0.0.0',debug=True)