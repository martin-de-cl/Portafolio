#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

    Mail Manager

    Modulo para utilizar la API de google  mail y extraer informacion
    Es necesario usar el sitio de google para obtener un Token de
    identidad para ser usado por el extractor

    @BY         : Martin Pimentel
    @Licencia   : MIT
    @Fecha      : 2024_05_15

"""
import base64
import random
import time
import weakref

from bs4 import BeautifulSoup

from time import sleep
from datetime import datetime as dt

from urllib import request, error as url_error
from os.path import abspath, exists as path_exists, join as join_path
from os import mkdir

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class MailManager():

    def __init__(self):

        self.GMAIL_SITE = ['https://www.googleapis.com/auth/gmail.readonly']
        self.CRED_FILE = abspath('../etc/credentials.json')
        self.TOKEN = abspath('../etc/token.json')

        self.SESSION_ID = self._generate_session_id()
        self.connection_status = self._internet_status()
        self.CREDENTIALS = self.check_credentials()

        self.MESSAGES = []

    def _internet_status(self) -> bool:
        try:
            request.urlopen('http://www.google.cl', timeout=1)
            return True
        except url_error.URLError as e:
            return False

    def check_credentials(self) -> str:

        credentianls = None
        if path_exists(self.TOKEN):
            credentianls = Credentials.from_authorized_user_file(self.TOKEN, self.GMAIL_SITE)

        if not credentianls or not credentianls.valid:
            if credentianls and credentianls.expired and credentianls.refresh_token:
                credentianls.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.CRED_FILE, self.GMAIL_SITE)
                credentianls = flow.run_local_server(port=0)
            with open(self.TOKEN, 'w') as token:
                token.write(credentianls.to_json())

        return credentianls

    def retrieve_information(self,creds=None):
        try:
            service = build('gmail', 'v1', credentials=self.CREDENTIALS)
            results = service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])
            if not labels:
                print('no labels found')
                return
            for label in labels:
                print(label['name'])
        except HttpError as error:
            print('This error happened {}'.format(error))

    def search_email(self, query=None):

        if query is None:
            subject         = 'Email Subject to look for'
            sender          = 'mail_sender@looking.for'
            read_state      = 'unread' #read
            last_capture    = ''

            query = 'from:{} AND is:{}'.format(sender, read_state)

        print('Query: {}'.format(query))

        service = build('gmail', 'v1', credentials=self.CREDENTIALS)
        result = service.users().messages().list(userId='me', q=query).execute()
        print(result)
        messages = result.get('messages',[])
        print(messages)

        message_count=0
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            email_data = msg['payload']['headers']
            for values in email_data:
                name = values['name']
                if name == 'From':
                    from_name = values['value']
                    for part in msg['payload']['parts']:
                        try:
                            data = part['body']['data']
                            byte_code = base64.urlsafe_b64decode(data)

                            text = byte_code.decode('utf-8')
                            print('\n\n[+] Email dump')
                            print("largo {}".format(len(text)))
                            print(dir(text))
                            print('Mensaje:\n{}'.format(self.parse_html(text)))
                            self.MESSAGES.append(text)
                        except BaseException as error:
                            pass

        return messages

    def search_for_verification_code(self, query=None):
        if query is None:
            subject         = 'specific subject 2'
            sender          = 'specific@domain.com'
            read_state      = 'email state' # read or unread
            last_capture    = ''

            query = 'subject:{} AND is:{}'.format(subject, read_state)

        print('Query: {}'.format(query))

        service = build('gmail', 'v1', credentials=self.CREDENTIALS)
        result = service.users().messages().list(userId='me', q=query).execute()
        print(result)
        messages = result.get('messages',[])
        print(messages)

        code = ''
        message_count=0

        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            email_data = msg['payload']['headers']
            for values in email_data:
                name = values['name']
                if name == 'From':
                    from_name = values['value']
                    code = msg['snippet'].split('Tu código de confirmación es: ')[1].rsplit(' Regresa')[0]
                    break
            if code != '':
                break
        print(code)
        return code

    def check_if_html_is_pressent(self, message)->bool:
        if bool(BeautifulSoup(message, "html.parser").find()):
            return True
        else:
            return False

    def parse_html(self, message):
        if self.check_if_html_is_pressent(message):
            soup = BeautifulSoup(message, features='html.parser')

            for script in soup(['script','style']):
                script.extract()

            plain_text = soup.get_text()

            # agregar mas funciones para mejorar el texto

            lines = (line.strip() for line in plain_text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            plain_text = '\n'.join(chunk for chunk in chunks if chunk)

            return plain_text

    def download_files(self, url:str, root_path:str, name:str):
        request.urlretrieve(url, filename=abspath(join_path(root_path ,name)))

    def main(self):
        creds=self.check_credentials()
        self.retrieve_information(creds)

    def print_messages(self):
        print('Printing Message:')
        print(len(self.MESSAGES))

    gmail_test = MailManager()
    gmail_test.retrieve_information()
    print('\n[+] Searching Emails')
    gmail_test.search_email()
    gmail_test.print_messages()
