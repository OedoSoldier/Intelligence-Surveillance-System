#!/usr/bin/env python

import boto3
import cv2
import numpy
import os
import base64
import gspread
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from httplib2 import Http
from time import localtime, strftime, time, sleep
from oauth2client.service_account import ServiceAccountCredentials
from apiclient import discovery, errors
from apiclient.discovery import build
from oauth2client import client
from oauth2client import tools
from oauth2client import file


def compare_faces(
        bucket,
        key,
        bucket_target,
        key_target,
        threshold=80,
        region='us-east-1'):
    '''
    Require for face comparision
    '''
    rekognition = boto3.client('rekognition', region)
    response = rekognition.compare_faces(
        SourceImage={
            'S3Object': {
                'Bucket': bucket,
                'Name': key,
            }
        },
        TargetImage={
            'S3Object': {
                'Bucket': bucket_target,
                'Name': key_target,
            }
        },
        SimilarityThreshold=threshold,
    )
    return response['SourceImageFace'], response['FaceMatches']


def upload_log(text):
    '''
    Upload the Alert time to the google drive sheet
    '''
    scope = ['https://spreadsheets.google.com/feeds']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        'ProjectLog-41cafcffcf13.json', scope)
    gc = gspread.authorize(credentials)
    wks = gc.open('ISeeU_Log').sheet1
    wks.append_row([text])


def send(service, user_id, message):
    '''
    Send the mime email package
    '''
    try:
        message = (
            service.users().messages().send(
                userId=user_id,
                body=message).execute())
        print('Message Id: %s' % message['id'])
        return message
    except errors.HttpError as error:
        print('An error occurred: %s' % error)


def create_email(sender, to, subject, message_text, pic):
    '''
    Create the email
    Included information: Sender, Receiver, Subject, Text, Attached Image
    '''
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['Subject'] = subject
    msg = MIMEText(message_text)
    message.attach(msg)

    fp = open(pic, 'rb')
    msg = MIMEImage(fp.read(), _subtype='jpeg')
    fp.close()
    imagename = os.path.basename(pic)
    msg.add_header('Content-Disposition', 'attachment', filename=imagename)
    message.attach(msg)

    return {'raw': base64.urlsafe_b64encode(message.as_string())}


def authenticate():
    '''
    Using oauth2 to get the credentials.
    It will give all permission related to gmail.
    client_secret.json is the secret key you get from google.
    Reference: Gmail API python quickstart
    '''
    SCOPES = 'https://mail.google.com'
    store = file.Storage('credentials.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = discovery.build('gmail', 'v1', http=creds.authorize(Http()))

    return service


def stranger_detected(pic):
    '''
    Recore the date time and make them as the code for the user the trigger
    alarm
    '''
    nowtime = strftime("%Y-%m-%d %H:%M:%S", localtime())
    trigcode = strftime("%d%H%M%S", localtime())

    # Upload log to Google drive
    text = 'Stranger show up at ' + nowtime
    upload_log(text)

    # Information of email
    # pic = 'guldan.jpg'  # Attached Image
    sender = "wenganq11@gmail.com"
    to = "wengq@bu.edu"  # User email address
    subject = "Alert from ISeeU!"
    text = text + '\nReply ' + trigcode + ' to trigger the alarm.'

    # Sending email to user
    service = authenticate()
    message = create_email(sender, to, subject, text, pic)
    send(service, 'me', message)
    return service, subject, trigcode


def main():
    while True:
        print('No face detected...')
        if os.path.isfile('face.jpg'):
            print('Face found!')
            bucket_name = 'ec500j1-project-iseeu'
            source_name = ['sh.jpg']  # User input faces
            target_name = 'face.jpg'  # Temporary image

            s3 = boto3.client('s3')
            # Upload images to s3 server
            for img in source_name:
                s3.upload_file(img, bucket_name, img)
            s3.upload_file(target_name, bucket_name, target_name)

            while True:
                try:
                    # Check if the images are successfully uploaded
                    for img in source_name:
                        boto3.resource('s3').Object(bucket_name, img).load()
                    boto3.resource('s3').Object(
                        bucket_name, target_name).load()
                except BaseException:
                    continue
                break

            sources, matches = {}, {}
            for img in source_name:
                try:
                    sources[img], matches[img] = compare_faces(
                        bucket_name, img, bucket_name, target_name)
                except Exception as e:
                    # If Rekognition failure
                    print('Rekognition error: ' + e)
                    os.remove('face.jpg')

                if len(matches[img]) == 0:
                    # Send notification email
                    service, target, trigcode = stranger_detected(
                        'face.jpg')
                    user_id = 'me'
                    flag = False  # Flag for trigger alert
                    st = time()
                    while time() - st < 120:  # Listen for 2 minutes
                        '''
                        Check all the email for user's reply every 30 seconds.
                        If the subject match, check if the trigcode match.
                        If the trigcode match too, return True to set off alarm.
                        '''
                        threads = service.users().threads().list(
                            userId=user_id).execute().get('threads', [])
                        for thread in threads:
                            tdata = service.users().threads().get(
                                userId=user_id, id=thread['id']).execute()
                            nmsgs = len(tdata['messages'])
                            msg = tdata['messages'][0]['payload']
                            subject = ''
                            for header in msg['headers']:
                                if header['name'] == 'Subject':
                                    subject = header['value']
                                    break
                            if subject == target:
                                if thread[u'snippet'][0:8] == trigcode:
                                    # If user replies with trigcode
                                    flag = True
                                    break
                        if flag:
                            # If user replies with trigcode
                            break
                        nt = strftime('%Y-%m-%d %H:%M:%S', localtime())
                        print('Still listening: ' + nt)
                        sleep(30)
                    print('Alert!')  # Emulated alert
                else:
                    print('Not a stranger')  # Do nothing

            # Delete all images from s3 server
            for img in source_name:
                s3.delete_object(Bucket=bucket_name, Key=img)
            s3.delete_object(Bucket=bucket_name, Key=target_name)

            os.remove('face.jpg')  # Delete temperary image

        sleep(10)


if __name__ == '__main__':
    main()
