import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_email(receiver, account, password):
    msg = MIMEMultipart()
    msg['From'] = 'pipixia.ca@outlook.com'
    msg['To'] = receiver
    msg['Subject'] = 'Welcome to the Party! ---From Pipixia'
    message = 'Welcome to the pipixia\'s domain!\n Your account name is: {0}\n Your login password is: {1} \n LONG LIVE THE MANTIS SHRIMP KING !'
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
    return
