import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from bs4 import BeautifulSoup

from authorisation import authorisation

class mail_operations():

    __creds = None
    __service = None

    def __get_sender(self, i: int, messages) -> str:
        last_message = messages[i]['payload']
        headers = last_message['headers']
        for details in headers:
            if details['name'] == 'From':
                sender = details['value']
        if sender == "project.dump.nabh@gmail.com" and len(messages) > i*-1:
            self.__get_sender(i-1, messages)
        return sender
    
    def __edit_content(self, text: str) -> str:
        new_text = ""
        test_list = text.split("\n")
        for i in test_list:
            if "On" in i and ("AM" in i or "PM" in i) and "wrote:" in i and "at" in i:
                break
            else:
                new_text += i
                new_text += "\n"
        return new_text

    def __init__(self):
        auth = authorisation()
        self.__creds = auth.cred_token_auth()
        self.__service = build("gmail", "v1", credentials = self.__creds)
    
    def read_mails(self) -> list | None:
        threads = self.__service.users().threads().list(userId='me', labelIds = ["INBOX", "UNREAD"]).execute().get('threads', [])
        emails = []
        for thread in threads:
            thread_details = self.__service.users().threads().get(userId='me', id=thread['id']).execute()
            messages = thread_details['messages']
            last_message = messages[-1]['payload']
            headers = last_message['headers']
            for details in headers:
                if details['name'] == 'Subject':
                    subject = details['value']
                elif details['name'] == 'From':
                    sender = details['value']
                    if sender == "project.dump.nabh@gmail.com":
                        sender = self.__get_sender(-2, messages)
            body = []
            content = ""
            if len(messages) > 1:
                message_type = "Thread"
                for message in messages:
                    payload = message['payload']
                    message_headers = payload['headers']
                    for message_details in message_headers:
                        if message_details['name'] == 'From':
                            if message_details['value'] == "project.dump.nabh@gmail.com":
                                content += "\nMessage from me:\n"
                            else:
                                content += f"\nMessage from {message_details['value']}:\n"
                    parts = message['payload'].get('parts')[0]
                    data = parts['body']['data']
                    data = data.replace("-","+").replace("_","/")
                    decoded_data = base64.b64decode(bytes(data, "UTF-8"))
                    soup = BeautifulSoup(decoded_data , "lxml")
                    text = soup.body.get_text()
                    formated_text = self.__edit_content(text)
                    content += formated_text
                body.append(content)
            else:
                message_type = "Single Mail"
                parts = last_message.get('parts')[0]
                data = parts['body']['data']
                data = data.replace("-","+").replace("_","/")
                decoded_data = base64.b64decode(bytes(data, "UTF-8"))
                soup = BeautifulSoup(decoded_data , "lxml")
                content += soup.body.get_text()
                body.append(content)
            emails.append({"ID" : thread['id'], "Type" : message_type, "Sender" : sender, "Subject" : subject, "Body" : body})
        return emails
    
    def send_mails(self, replies: list):
        for reply in replies:
            if reply["Reply"].lower() != "no reply required":
                thread = self.__service.users().threads().get(userId = 'me', id = reply["ID"]).execute()
                messages = thread['messages'][0]['payload']['headers']

                # Retrieve the metadata of the thread
                for msg in messages:
                    if msg['name'] == 'Message-ID':
                        message_id = msg['value']

                # Constructing the reply message
                message = MIMEMultipart()
                msg = MIMEText(reply["Reply"])
                message.attach(msg)
                message['To'] = reply["Sender"]
                message['Subject'] = reply["Subject"]
                message['References '] = message_id
                message['In-Reply-To '] = message_id

                encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

                create_message = {'raw': encoded_message, 'threadId': reply["ID"]}
                # Sending the reply message to the thread
                send_message = (self.__service.users().messages().send(userId="me", body=create_message).execute())
            self.__service.users().threads().modify(userId = 'me', id = reply["ID"],body = { 'removeLabelIds': ['UNREAD']}).execute()