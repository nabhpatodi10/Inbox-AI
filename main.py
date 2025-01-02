from dotenv import load_dotenv
load_dotenv()
from langchain_groq import ChatGroq
from langchain.schema.runnable import RunnableLambda

import nodes
import structures

node = nodes.nodes()
structure = structures.structures()

model = ChatGroq(model = "llama-3.3-70b-versatile")

reply_decision_chain = node.reply_decision_node | model.with_structured_output(structure.decision_output)

classification_chain = node.classification_node | model.with_structured_output(structure.classification_output)

reply_writing_chain = node.reply_writing_node | model.with_structured_output(structure.reply_output)

hallucination_check_chain = node.hallucination_check_node | model.with_structured_output(structure.decision_output)

content_check_chain = node.content_check_node | model.with_structured_output(structure.decision_output)

user = "Nabh Patodi"

information = "I am a third year student pursuing B.Tech Computer Science and Engineering from S.R.M Institute of Science and Technology"

email_classes = "'positive feedback', 'negative feedback', 'general email', 'marketing or social spam', 'escalate to human'"

email1 = """Hi Nabh,
        I hope you're doing well. Just wanted to check in on you. I heard about your co-op offer, huge congratulations to you for that.
        Hope everyone in the family is fine. Let me know if you need any help.
        
        Best wishes
        Ananya"""

email2 = """Hello sir,
        We are from ElectroSteel Pvt Ltd, the following are this month's rates for wire rod:
        5 mm = ₹5500
        6 mm = ₹6500
        7 mm = ₹7500
        
        Let us know if you have any requirements."""

email3 = """Hello user,
        This is Team Instagram, Please find the summary of your earnings for this month. If you have any doubts, reach out to us at insta@insta.com"""

email = """Hello sir
        We recently got to know that you are a student and we would want to work with you, below is the list of services we provide:
        AI-ML Training
        Cloud and DevOps Training
        Internship Programmes
        
        Please let us know if you would want any services from us."""

email5 = """Nabh, it's an emergency. Your grandfather has been admitted to the hospital and he's critical, the doctors are saying that he has very less 
        time left. I think you should come here and be with him."""

def email_classification(decision):
    print("Reply Decision: ", decision)
    if decision.decision == True:
        return classification_chain.invoke({"user" : user, "information" : information, "email_classes" : email_classes, "email" : email})
    else:
        return "No Reply Required"
    
def reply_writing(email_class):
    print("Email Class: ", email_class)
    if email_class == "No Reply Required":
        return email_class
    else:
        return reply_writing_chain.invoke({"email_class" : email_class.email_class, "user" : user, "information" : information, "email" : email})
    
def hallucination_check(reply):
    if reply == "No Reply Required":
        return reply
    else:
        return {"decision" : hallucination_check_chain.invoke({"email" : email, "reply" : reply.reply}), "reply" : reply}
    
def content_check(decision):
    if decision == "No Reply Required":
        return decision
    elif decision["decision"].decision == True:
        return content_chain_call()
    else:
        return {"decision" : content_check_chain.invoke({"user" : user, "information" : information, "email" : email, "reply" : decision["reply"].reply}), "reply" : decision["reply"]}
    
def chain_end(decision):
    if decision == "No Reply Required":
        return decision
    elif decision["decision"].decision == False:
        return final_chain_call()
    else:
        return decision["reply"].reply
    
final_chain = reply_decision_chain | RunnableLambda(email_classification) | RunnableLambda(reply_writing) | RunnableLambda(hallucination_check) | RunnableLambda(content_check) | RunnableLambda(chain_end)

def final_chain_call():
    return final_chain.invoke({"user" : user, "information" : information, "email" : email})

def content_chain_call():
    chain = reply_decision_chain | RunnableLambda(email_classification) | RunnableLambda(reply_writing) | RunnableLambda(hallucination_check) | RunnableLambda(content_check)
    return chain.invoke({"user" : user, "information" : information, "email" : email})

print()
print(final_chain_call())