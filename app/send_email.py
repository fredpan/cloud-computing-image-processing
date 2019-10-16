import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

#This function use POP to send an email to the new user with their registrated
#user name and the password.
def send_email(receiver, account, password):
    try:
        msg = MIMEMultipart()
        msg['From'] = 'pipixia.ca@outlook.com'
        msg['To'] = receiver
        msg['Subject'] = 'Welcome to Image Text Identification Process Engine ----ECE1779 Project1'
        message = 'Welcome to Image Text Identification Process Engine\n Your account name is: {0}\n Your login password is: {1} \n Thanks for the registeration.'
        message = message.format(account, password)
        msg.attach(MIMEText(message))

        mailserver = smtplib.SMTP('smtp.office365.com', 587)
        # identify ourselves to smtp gmail client
        mailserver.ehlo()
        # secure our email with tls encryption
        mailserver.starttls()
        # re-identify ourselves as an encrypted connection
        mailserver.ehlo()
        mailserver.login('pipixia.ca@outlook.com', 'Ece_1779')
        mailserver.sendmail('pipixia.ca@outlook.com', receiver, msg.as_string())
        mailserver.quit()
    except Exception as ex:
        print(ex)
        return False

    return True
