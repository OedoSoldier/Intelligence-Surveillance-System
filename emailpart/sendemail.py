## Copyright 2018 Ganquan Wen  wengq@bu.edu
import smtplib
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from time import gmtime, strftime
from oauth2client.service_account import ServiceAccountCredentials
import gspread

pic = 'guldan.jpg'  # the pic took by camera
# trying to use imap
def sendMail(body, image):
	server = smtplib.SMTP('smtp.gmail.com', 587)
	server.ehlo()
	server.starttls()
	server.login("wenganq11@gmail.com", "password")
 
	msg = MIMEMultipart()
	msg["To"] = "wengq@bu.edu"
	msg["From"] = "wenganq11@gmail.com"
	msg["Subject"] = 'Alert from ISeeU'

	msg.attach(MIMEText(body, 'html', 'utf-8'))   # Added, and edited the previous line

	with open(image, 'rb') as f:
		msgImage = MIMEImage(f.read(), _subtype="jpeg")

	msgImage.add_header('Pic_ID', '<image1>')
	msg.attach(msgImage)



	server.sendmail("wenganq11@gmail.com", "wengq@bu.edu", msg.as_string())
	server.quit()


def upload_log(text):
	scope=['https://spreadsheets.google.com/feeds']
	credentials=ServiceAccountCredentials.from_json_keyfile_name('ProjectLog-41cafcffcf13.json', scope)
	gc=gspread.authorize(credentials)
	wks=gc.open('ISeeU_Log').sheet1
	wks.append_row([text])

def main():
	# stranger is a flag to indicate the result of face recognition
	stranger = 1
	if stranger == 1:
		print ('Alert sent!')
		nowtime = strftime("%Y-%m-%d %H:%M:%S", gmtime())
		text = 'Alert at ' + nowtime
		sendMail(text, pic)
		upload_log(text)


if __name__ == '__main__':
	main()


# it will take about 17s to send the picture to the user through email