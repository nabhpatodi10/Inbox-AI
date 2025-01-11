from dotenv import load_dotenv
load_dotenv()
from langchain.schema.runnable import RunnableLambda

from email_operations import mail_operations
from chains import mail_chains, thread_chains

emails = mail_operations()
chain_type = mail_chains()

user = "Nabh Patodi"

information = "I am a third year student pursuing B.Tech Computer Science and Engineering from S.R.M Institute of Science and Technology"

email_classes = """'positive feedback' - Any kind of a positive feedback regarding a product or a service\n
                'negative feedback' - Any kind of a negative feedback regarding a product or a service\n
                'general email' - Any email from family or friend or a general informative email from someone\n
                'marketing or social email' - Any email from any social media platform or any other source which has the only aim of marketing or 
                selling something\n
                'escalate to human' - Any email which tells about an emergency or any situation which needs the attention of the owner"""

mails = emails.read_mails()

def email_classification(decision):
    if decision.decision == True:
        return chain_type.classification_chain.invoke({"user" : user, "information" : information, "email_classes" : email_classes, "email" : email})
    else:
        return "No Reply Required"
    
def reply_writing(email_class):
    print("In Writing Node", end = "\n")
    if email_class == "No Reply Required":
        return email_class
    elif "escalate to human" in email_class.email_class.lower():
        return "Escalate to Human"
    else:
        print("Writing Reply", end = "\n")
        return chain_type.reply_writing_chain.invoke({"email_class" : email_class.email_class, "user" : user, "information" : information, "email" : email})
    
def hallucination_check(reply):
    print("In Hallucination Check Node", end = "\n")
    if isinstance(reply, str):
        return reply
    else:
        print("Checking Hallucination", end = "\n")
        return {"decision" : chain_type.hallucination_check_chain.invoke({"email" : email, "reply" : reply.reply}), "reply" : reply}
    
def content_check(decision):
    print("In Content Check Node", end = "\n")
    if isinstance(decision, str):
        return decision
    elif decision["decision"].decision == True:
        print("Hallucination Found", end = "\n")
        return content_chain_call()
    else:
        print("Checking checking content", end = "\n")
        return {"decision" : chain_type.content_check_chain.invoke({"user" : user, "information" : information, "email" : email, "reply" : decision["reply"].reply}), "reply" : decision["reply"]}
    
def chain_end(decision):
    print("Ending Chain", end = "\n")
    if isinstance(decision, str):
        return decision
    elif decision["decision"].decision == False:
        return final_output()
    else:
        return decision["reply"].reply
    
final_chain = chain_type.reply_decision_chain | RunnableLambda(email_classification) | RunnableLambda(reply_writing) | RunnableLambda(hallucination_check) | RunnableLambda(content_check) | RunnableLambda(chain_end)

def final_output():
    global email
    global chain_type
    replies = []
    try:
        j = 1
        for mail in mails:
            if mail["Type"] == "Single Mail":
                chain_type = mail_chains()
            elif mail["Type"] == "Thread":
                chain_type = thread_chains()
            print(f"Thread {j}: \n")
            email = "Sender: " + mail["Sender"] + "\nSubject: " + mail["Subject"] + "\nEmail Body:"
            for i in mail["Body"]:
                email += i + "\n\n"
            print(email, end = "\n")
            if "<" in mail["Sender"] and ">" in mail["Sender"]:
                start = mail["Sender"].index("<")
                sender_mail = mail["Sender"][start + 1 : -1]
            reply = final_chain.invoke({"user" : user, "information" : information, "email" : email})
            replies.append({"ID": mail["ID"], "Sender" : sender_mail, "Subject" : mail["Subject"], "Reply" : reply})
            j+=1
        return replies
    except Exception as e:
        print(e)

def content_chain_call():
    chain = chain_type.reply_decision_chain | RunnableLambda(email_classification) | RunnableLambda(reply_writing) | RunnableLambda(hallucination_check) | RunnableLambda(content_check)
    return chain.invoke({"user" : user, "information" : information, "email" : email})

print()
all_replies = final_output()
print()
for i in all_replies:
    print(i["Reply"], end = "\n")

emails.send_mails(all_replies)