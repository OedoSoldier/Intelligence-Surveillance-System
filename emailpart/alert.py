import base64
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from httplib2 import Http
from time import localtime, strftime, time, sleep
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client import file
from apiclient.discovery import build
from apiclient import errors


def upload_log(text):
	'''
	Upload the Alert time to the google drive sheet
	'''
	scope=['https://spreadsheets.google.com/feeds']
	credentials=ServiceAccountCredentials.from_json_keyfile_name('ProjectLog-41cafcffcf13.json', scope)
	gc=gspread.authorize(credentials)
	wks=gc.open('ISeeU_Log').sheet1
	wks.append_row([text])


def send(service, user_id, message):
	'''
	send the mime email package
	'''
	try:
		message = (service.users().messages().send(userId=user_id, body=message).execute())
		print ('Message Id: %s' % message['id'])
		return message
	except errors.HttpError, error:
		print ('An error occurred: %s' % error)


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


def listen_to_trig(service, target, trigcode, user_id='me'):
	'''
    Check all the email for user's reply every 60 seconds.
    If the subject match, check if the trigcode match.
    If the trigcode match too, return True to set off alarm.
    '''
	st = time()
	while time() - st < 3601:  # Listen for an hour
		
		threads = service.users().threads().list(userId=user_id).execute().get('threads', [])
		for thread in threads:
			tdata = service.users().threads().get(userId=user_id, id=thread['id']).execute()
			nmsgs = len(tdata['messages'])
			msg = tdata['messages'][0]['payload']
			subject = ''
			for header in msg['headers']:
				if header['name'] == 'Subject':
					subject = header['value']
					break
			if subject == target:
				if thread[u'snippet'][0:8] == trigcode:
					print 'Alarm on!'
					return True
		nt = strftime("%Y-%m-%d %H:%M:%S", localtime())	
		print 'Still listening' + nt
		sleep(60)



def stranger_detected():  # stranger_detected(pic)
	# Recore the date time and make them as the code for the user the trigger alarm
	nowtime = strftime("%Y-%m-%d %H:%M:%S", localtime())
	trigcode = strftime("%d%H%M%S", localtime())

	# Upload log to Google drive
	text = 'Stranger show up at ' + nowtime
	upload_log(text)

	# Information of email
	pic = 'guldan.jpg'  # Attached Image
	sender = "wenganq11@gmail.com"
	to = "wengq@bu.edu"  # User email address
	subject = "Alert from ISeeU!"
	text = text + '\nReply ' + trigcode + ' to trigger the alarm.'

	# Sending email to user
	service = authenticate()
	message = create_email(sender, to, subject, text, pic)
	send(service, 'me', message)
	listen_to_trig(service, subject, trigcode)


def main():
	stranger = 1
	if stranger == 1:
		stranger_detected()

if __name__ == '__main__':
	main()


