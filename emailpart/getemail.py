import base64
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import mimetypes
import os
#from __future__ import print_function
from httplib2 import Http
import os
import email

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools
from oauth2client import file
from apiclient.discovery import build

from apiclient import errors

from apiclient import errors

def show_chatty_threads(service, target, user_id='me'):
    threads = service.users().threads().list(userId=user_id).execute().get('threads', [])
    for thread in threads:
        tdata = service.users().threads().get(userId=user_id, id=thread['id']).execute()
        nmsgs = len(tdata['messages'])

        if nmsgs > 0:    # skip if <3 msgs in thread
            msg = tdata['messages'][0]['payload']
            subject = ''
            for header in msg['headers']:
                if header['name'] == 'Subject':
                    subject = header['value']
                    break
            print('- %s (%d msgs)' % (subject, nmsgs))
            #if subject == 'Your password changed':
            if subject == target:
                return thread, thread['id']


def main():

  SCOPES = 'https://mail.google.com'
  store = file.Storage('credentials.json')
  creds = store.get()
  if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
    creds = tools.run_flow(flow, store)
  service = discovery.build('gmail', 'v1', http=creds.authorize(Http()))


  target = 'alarm'
  threads, tid = show_chatty_threads(service, target, user_id='me')
  print threads[u'snippet']
  print tid


if __name__ == '__main__':
	main()
