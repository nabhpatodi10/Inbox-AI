from fastapi import FastAPI
import uvicorn
from dotenv import load_dotenv
load_dotenv()

from email_operations import mail_operations
from chains import chain_functions
from database import database
from structures import structures

app = FastAPI()

emails = mail_operations()
db = database()

@app.get("/")
def home():
    return {"Home Page" : "Welcome to Inbox-AI"}

@app.post("/login")
def login(username: str) -> dict:
    details = db.get(username)
    if details is None:
        return {"Error" : "Incorrect Username"}
    user = details["fullname"]
    email = details["email_id"]
    information = details["user_information"]
    email_classes = details["email_classes"]
    settings = details["settings"]
    send_mails = settings["send_mails_directly"]
    mark_mails = settings["mark_mails_read"]
    status = mail_func(user, information, email, email_classes, send_mails, mark_mails)
    return {"Data" : f"Welcome {user}", "Status" : status}

@app.post("/signup")
def signup(details: structures.signup_input) -> dict:
    user = details.fullname
    email = details.email
    information = details.user_information
    email_classes = details.email_classes
    send_mails = details.send_mails
    mark_mails = details.mark_mails
    value = db.insert(details.username, user, email, information, email_classes, send_mails, mark_mails)
    if value:
        status = mail_func(user, information, email, email_classes, send_mails, mark_mails)
        return {"Data" : f"Signup Successful! Welcome {user}", "Status" : status}
    else:
        return {"Data" : "Signup Unsuccessful! Try Later..."}

@app.post("/delete")
def delete(username: str) -> dict:
    value = db.delete(username)
    if value:
        return {"Data" : "Account Deleted... Hate to see you go"}
    else:
        return {"Data" : "Account could not be deleted, try later..."}

@app.post("/update")
def update(username: str, data: dict):
    value = db.update(username, data)
    if value:
        return {"Data" : "Update Successful"}
    else:
        return {"Data" : "Update Unsuccessful"}

def mail_func(user: str, information: str, email: str, email_classes: str, send_mails: bool, mark_mails: bool) -> dict:

    status = {}

    mails = emails.read_mails(email, True)

    if len(mails) == 0:
        return {"Data" : "No Unread Mails"}
    
    status["Emails Read"] = "Successful"

    chain_function = chain_functions(user, information, email_classes, mails)

    print()
    all_replies = chain_function.final_output()
    if len(all_replies) == 0:
        status["Replies Generated"] = "No Replies Generated"
        return status
    print()
    for i in all_replies:
        print(i["Reply"], end = "\n")

    status["Replies Generated"] = f"{len(all_replies)} Replies Generated"

    if emails.send_mails(all_replies, send_mails, mark_mails):
        status["Mails Sent"] = "Successful"
        return status
    
    status["Mails Sent"] = "Unsuccessful"
    return status

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)