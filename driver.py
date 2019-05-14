#1. wait for new unread email
#2. read email, parse data
#3. ???
#4. profit

import smtplib
import time
import imaplib
import email
import requests
import csv
import datetime
from twilio.rest import Client
from twilio.twiml.voice_response import Gather, VoiceResponse, Say
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

#DATA
ORG_EMAIL   = "@gmail.com"
FROM_EMAIL  = "####" + ORG_EMAIL
TO_EMAIL    = "####" + ORG_EMAIL
FROM_PWD    = "####"
IMAP_SERVER = "imap.gmail.com"
IMAP_PORT   = 993
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT   = 465

#TOKENS
account_sid = "####"
auth_token  = "####"
flow_url = "https://studio.twilio.com/v1/Flows/####/"



def sendMail(toaddr):
    fromaddr = "#### t+e+-st@gmail.com"
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "LOG File"

    body = "Alert level: CRITICAL \nAlert message: Unauthorized server access \nAsset: CBHQ-04562 \nAsset owner: John Doe \nAsset email: catalin@cybourn.com \nAsset phone: +40727042452"
    msg.attach(MIMEText(body, 'plain'))

    filename = "logs.csv"
    attachment = open("logs.csv", "rb")


    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= %s" % "logs.csv")

    msg.attach(part)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(fromaddr, "####")
    text = msg.as_string()
    server.sendmail(fromaddr, fromaddr, text)

    server.quit()

def triggerAlert(phoneNumber, emailAdress):
    client = Client(account_sid, auth_token)

    execution = client.studio \
                  .flows('####') \
                  .executions \
                  .create(to=phoneNumber, from_='+####')

    #log exec id
    try:
        myFile = open('logs.csv', 'wb')
        with myFile:
            data = ["Exec id", execution.sid, datetime.datetime.now()]
            writer = csv.writer(myFile)
            writer.writerow(data)
            print "Successfuly written to log"
    except:
        print "Could not write to log"

    #send mail to analyst with logs
    sendMail(emailAdress)

"""
def callOwner():
    client = Client(account_sid, auth_token)
    client.calls.create(url="https://handler.twilio.com/twiml/####",
                        to='+####',
                        from_='+####')



def sendSms():
    client = Client(account_sid, auth_token)

    client.messages.create(to="+####",
                           from_="+####",
                           body="Unauthorized server access. Reply to confirm.")
"""

def get_text(msg):
    if msg.is_multipart():
        return get_text(msg.get_payload(0))
    else:
        return msg.get_payload(None, True)

def readMail():
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(FROM_EMAIL,FROM_PWD)
        mail.select('inbox')
        type, data = mail.search(None, 'ALL', '(UNSEEN)')
        mail_ids = data[0]

        print len(mail_ids)

        id_list = mail_ids.split()

        for i in id_list:
            typ, data = mail.fetch(i, '(RFC822)' )

            for response_part in data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_string(response_part[1])
                    email_subject = msg['subject']
                    msgg = get_text(msg)
                    print msgg

                    if email_subject == "[CYBOURN-00001] SIEM ALERT - Critical":
                        try:
                            myFile = open('logs.csv', 'wb')
                            with myFile:
                                data = ["Notification", email_subject, datetime.datetime.now()]
                                writer = csv.writer(myFile)
                                writer.writerow(data)
                                print "Successfuly written to log"
                        except:
                            print "Could not write to log"
                        triggerAlert("+####", "FROM_EMAIL")
    except:
        print "No new notifications"


starttime=time.time()
while True:
  print "Reading mail..."
  readMail()
  time.sleep(30.0 - ((time.time() - starttime) % 30.0))
