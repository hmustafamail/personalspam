#!/usr/bin/env python3

"""
Puts some "personalized" spam in your gmail Drafts folder for sending.

Mustafa Hussain

Usage:
personalspam.py contacts.csv message.txt "subject line"

Adapted https://developers.google.com/gmail/api/guides/drafts to Python 3. Was difficult.
"""

from __future__ import print_function
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import csv
from email.mime.text import MIMEText as MT
import base64
import sys
import json

def create_message(sender, to, subject, message_text):
    """Create a message for an email.

    Args:
    sender: Email address of the sender.
    to: Email address of the receiver.
    subject: The subject of the email message.
    message_text: The text of the email message.

    Returns:
    An object containing a base64url encoded email object.
    """
    message = MT(message_text)
    
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    raw = base64.urlsafe_b64encode(message.as_bytes())
    raw = raw.decode()
    return {'raw': raw}
    
def create_draft(service, user_id, message_body):
    """Create and insert a draft email. Print the returned draft's message and id.

    Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    message_body: The body of the email message, including headers.

    Returns:
    Draft object, including draft id and message meta data.
    """
    try:
        message = {'message': message_body}

        draft = service.users().drafts().create(userId=user_id, body=message).execute()

        print('Draft id: %s\nDraft message: %s' % (draft['id'], draft['message']))

        return draft

    except:
        e = sys.exc_info()[0]
        print('An error occurred in create_draft: %s' % e)
        return None

def setupAPI():
    """Sets up the Gmail API.
    """

    # This should work but it doesn't grant enough permissions.
    #SCOPES = 'https://www.googleapis.com/auth/gmail.compose'

    # So let's go with "just give me all the permissions."
    SCOPES = 'https://mail.google.com/'

    store = file.Storage('/path/to/credentials.json')
    creds = store.get()

    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('/path/to/client_secret.json', SCOPES)
        creds = tools.run_flow(flow, store)
    
    service = build('gmail', 'v1', http=creds.authorize(Http()))
    return service

def getContactGenerator(contactsfile):
    """Reads in contacts from CSV and generates one row-dictionary at a time.
    """

    with open(contactsfile, 'r') as csvfile:
        dict1 = csv.DictReader(csvfile, delimiter=',')

        for row in dict1:
            yield row

def main(contactsfile, contentfile, subject):
    """Composes the emails"""
    
    # Setup the Gmail API
    service = setupAPI()

    # Get the message that we will send
    with open(contentfile, 'r') as content_file:
        content = content_file.read()

    # Put our signature on the email.
    content = content + "\n\nEver So Sincerely,\nYour Name"

    # Get ready to read in the contacts
    contactGenerator = getContactGenerator(contactsfile)

    # Construct each message and store them in Drafts
    for contact in contactGenerator:
        
        # Put the greeting in the email
        thiscontent = "Hi " + contact["givenname"] + ",\n\n" + content

        # Create the message object
        message = create_message("youremailhere@gmaildomain.com", contact['email'], subject, thiscontent)

        # Store it as a draft.
        create_draft(service, 'me', message)
    
if __name__ == '__main__':
    
    try:
        contactsfile = sys.argv[1]
        contentfile = sys.argv[2]
        subject = sys.argv[3]
    
    except:
        print('Usage: personalspam.py contacts.csv message.txt "subject line"')
        exit()

    main(contactsfile, contentfile, subject)
