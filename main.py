from dotenv import load_dotenv
load_dotenv()

from email_operations import mail_operations
from chains import chain_functions
from database import database

emails = mail_operations()
db = database()

if db.connect_to_database():

    print("Options\n1. Login\n2. Signup\n3. Delete Account")
    choice = int(input("Enter your choice: "))
    username = input("Enter Username: ")

    if choice == 1:
        details = db.get(username)
        user = details["fullname"]
        information = details["user_information"]
        email_classes = details["email_classes"]
        print("Welcome", user)

    elif choice == 2:
        user = input("Full Name: ")
        email = input("Email: ")
        information = input("Information: ")
        email_classes = input("Email Classes: ")
        value = db.insert(username, user, email, information, email_classes)
        if value:
            print("Signup Successful!\nWelcome", user)
        else:
            print("Signup Unsuccessful! Try Later...")
            exit()

    elif choice == 3:
        value = db.delete(username)
        if value:
            print("Account Deleted... Hate to see you go")
        else:
            print("Account could not be deleted, try later...")
        exit()
    
    else:
        print("Invalid choice")
        exit()

    mails = emails.read_mails()

    if len(mails) == 0:
        print("No Unread Mails")
        exit()

    chain_function = chain_functions(user, information, email_classes, mails)

    print()
    all_replies = chain_function.final_output()
    print()
    for i in all_replies:
        print(i["Reply"], end = "\n")

    emails.send_mails(all_replies)