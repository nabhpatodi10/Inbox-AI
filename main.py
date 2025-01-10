from dotenv import load_dotenv
load_dotenv()
from langchain_groq import ChatGroq
from langchain.schema.runnable import RunnableLambda

from nodes import nodes
from structures import structures
from read_emails import read_emails

node = nodes()
structure = structures()
emails = read_emails()

model = ChatGroq(model = "llama-3.3-70b-versatile")

reply_decision_chain = node.reply_decision_node | model.with_structured_output(structure.decision_output)

classification_chain = node.classification_node | model.with_structured_output(structure.classification_output)

reply_writing_chain = node.reply_writing_node | model.with_structured_output(structure.reply_output)

hallucination_check_chain = node.hallucination_check_node | model.with_structured_output(structure.decision_output)

content_check_chain = node.content_check_node | model.with_structured_output(structure.decision_output)

user = "Nabh Patodi"

information = "I am a third year student pursuing B.Tech Computer Science and Engineering from S.R.M Institute of Science and Technology"

email_classes = """'positive feedback' - Any kind of a positive feedback regarding a product or a service\n
                'negative feedback' - Any kind of a negative feedback regarding a product or a service\n
                'general email' - Any email from family or friend or a general informative email from someone\n
                'marketing or social email' - Any email from any social media platform or any other source which has the only aim of marketing or 
                selling something\n
                'escalate to human' - Any email which tells about an emergency or any situation which needs the attention of the owner"""

mails = emails.read_mails()
global email
email = ""

def email_classification(decision):
    if decision.decision == True:
        return classification_chain.invoke({"user" : user, "information" : information, "email_classes" : email_classes, "email" : email})
    else:
        return "No Reply Required"
    
def reply_writing(email_class):
    if email_class == "No Reply Required":
        return email_class
    elif "escalate to human" in email_class.email_class.lower():
        return "Escalate to Human"
    else:
        return reply_writing_chain.invoke({"email_class" : email_class.email_class, "user" : user, "information" : information, "email" : email})
    
def hallucination_check(reply):
    if isinstance(reply, str):
        return reply
    else:
        return {"decision" : hallucination_check_chain.invoke({"email" : email, "reply" : reply.reply}), "reply" : reply}
    
def content_check(decision):
    if isinstance(decision, str):
        return decision
    elif decision["decision"].decision == True:
        return content_chain_call()
    else:
        return {"decision" : content_check_chain.invoke({"user" : user, "information" : information, "email" : email, "reply" : decision["reply"].reply}), "reply" : decision["reply"]}
    
def chain_end(decision):
    if isinstance(decision, str):
        return decision
    elif decision["decision"].decision == False:
        return final_output()
    else:
        return decision["reply"].reply
    
final_chain = reply_decision_chain | RunnableLambda(email_classification) | RunnableLambda(reply_writing) | RunnableLambda(hallucination_check) | RunnableLambda(content_check) | RunnableLambda(chain_end)

def final_output():
    replies = []
    try:
        for mail in mails:
            email = "Sender: " + mail["Sender"] + "\nSubject: " + mail["Subject"] + "\nBody: " + mail["Body"]
            print(email, end = "\n")
            reply = final_chain.invoke({"user" : user, "information" : information, "email" : email})
            replies.append({"ID": mail["ID"], "Reply" : reply})
        return replies
    except Exception as e:
        print(e)

def content_chain_call():
    chain = reply_decision_chain | RunnableLambda(email_classification) | RunnableLambda(reply_writing) | RunnableLambda(hallucination_check) | RunnableLambda(content_check)
    return chain.invoke({"user" : user, "information" : information, "email" : email})

print()
all_replies = final_output()
for i in all_replies:
    print(i["Reply"], end = "\n")