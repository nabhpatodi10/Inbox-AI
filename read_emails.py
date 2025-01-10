import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from bs4 import BeautifulSoup

from authorisation import authorisation

class read_emails():

    __creds = None
    __service = None

    def __init__(self):
        auth = authorisation()
        self.__creds = auth.cred_token_auth()
        self.__service = build("gmail", "v1", credentials=self.__creds)

    def read_mails(self):
        result = self.__service.users().messages().list(userId = 'me', labelIds = ["INBOX", "UNREAD"]).execute()
        messages = result.get('messages')
        emails = []
        for msg in messages:
            txt = self.__service.users().messages().get(userId = 'me', id = msg['id']).execute()
            try:
                payload = txt['payload']
                headers = payload['headers']
                for d in headers:
                    if d['name'] == 'Subject':
                        subject = d['value']
                    if d['name'] == 'From':
                        sender = d['value']
                parts = payload.get('parts')[0]
                data = parts['body']['data']
                data = data.replace("-","+").replace("_","/")
                decoded_data = base64.b64decode(bytes(data, "UTF-8"))
                soup = BeautifulSoup(decoded_data , "lxml")
                body = soup.body.get_text()
                emails.append({"ID" : msg['id'], "Sender" : sender, "Subject" : subject, "Body" : body})
            except Exception as error:
                print(error)
                return
        return emails