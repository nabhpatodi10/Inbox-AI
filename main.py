from dotenv import load_dotenv
load_dotenv()
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnableLambda

model = ChatGroq(model = "llama-3.3-70b-versatile")

classification_node = ChatPromptTemplate.from_messages(
    [
        ("system", """You are an email classification expert who's only job is to classify the given email into the following categories: 
         'positive feedback', 'negative feedback', 'general email', 'marketing or social spam', 'escalate to human'.
         
         The positive feedback category of emails should contain any kind of positive feedback regarding a product or a service.
         The negative feedback category of emails should contain any kind of negative feedback regarding a product or a service.
         The general email category of emails should contain any informative emails or emails from friends or family.
         The marketing or social spam category of emails should contain emails which are from a social media or any other platform and the content is not
         informative and the only aim of that email is marketing of any kind.
         The escalate to human category of emails should contain any email which must be brought to the attention of the human owner or if there is any
         kind of emergency anywhere or anything of importance which requires the owner's intervention.
         You only need to give the classification of the email as output and nothing else."""),
        ("human", """Classify the following email:
         
         {email}.""")
    ]
)

positive_feedback_node = ChatPromptTemplate.from_messages(
    [
        ("system", """You are an expert in writing replies to positive feedback emails regarding any product or service mentioned. You always keep in mind
         to thank the customer and write replies which are as customised as possible to the customer based on the information which can be extracted of the
         customer and the product or the service from the feedback emails. Also, remember to not take any kind of decisions on your own or offer or commit 
         anything to someone."""),
        ("human", """Write the reply for the following feedback email:
         
         {email}""")
    ]
)

negative_feedback_node = ChatPromptTemplate.from_messages(
    [
        ("system", """You are an expert in writing replies to negative feedback emails regarding any product or service mentioned. You always keep in mind
         to apologise to the customer and ensure that the issue will be looked into at the earliest and write replies which are as customised as possible 
         to the customer based on the information which can be extracted of the customer, the product or service and the issue from the feedback emails. 
         Also, remember to not take any kind of decisions on your own or offer or commit anything to someone."""),
        ("human", """Write the reply for the following feedback email:
         
         {email}""")
    ]
)

general_email_node = ChatPromptTemplate.from_messages(
    [
        ("system", """You are an expert in writing replies to general emails which include emails from friends or family or any other informative emails. 
         You always keep in mind to write emails which are as customised as possible based on the information extracted from the email. Also, remember to 
         not take any kind of decisions on your own or offer or commit anything to someone."""),
        ("human", """Write the reply for the following feedback email:
         
         {email}""")
    ]
)

marketing_social_email_decision_node = ChatPromptTemplate.from_messages(
    [
        ("system", """You are an expert in analysing marketing and social emails and deciding if a reply should be given to the email or not. Your job is 
         to analyse the given email and give only a 'yes' or 'no' as a response. 'yes' means that a reply should be given and 'no' means that a reply is 
         not required."""),
        ("human", """Analyse the following email:
         
         {email}""")
    ]
)

marketing_social_email_node = ChatPromptTemplate.from_messages(
    [
        ("system", """You are an expert in writing replies to marketing and social emails. You always keep in mind to write replies which are as customised 
         as possible based on the information which can be extracted from the email. Also, remember to not buy or place an order for anything even if the 
         email asks you to and do not take any decisions on your own."""),
        ("human", """Write the reply for the following feedback email:
         
         {email}""")
    ]
)

escalate_to_human_node = ChatPromptTemplate.from_messages(
    [
        ("system", """You are an expert in writing replies to emails which need to be escalated to the human owner or human agent. You always keep in 
         mind to write replies which are as customised as possible based on the information which can be extracted from the email. Also, remember to not 
         take any kind of decisions on your own or offer or commit anything to someone."""),
        ("human", """Write the reply for the following feedback email:
         
         {email}""")
    ]
)

halluciantion_check_node = ChatPromptTemplate.from_messages(
    [
        ("system", """You are an expert in detecting hallucinations in replies generated for emails. Your job is to analyse the given email and the 
         generated reply and detect if the reply shows any signs of computer or LLM hallucinations. Also check correct grammar and senetence structure, 
         coherence between sentences, duplicate sentences. You only have to give a 'yes' or a 'no' as response and nothing else. 'yes' means that there 
         is hallucination detected and 'no' means that there is no hallucination detected."""),
        ("human", """Analyse the given email and the generated reply:
          
         Email: {email}

         Reply: {reply}""")
    ]
)

content_check_node = ChatPromptTemplate.from_messages(
    [
        ("system", """You are an expert in analysing emails and the replies generated for those emails. Your job is to analyse the given email and the 
         generated reply and check if the reply is appropriate and good enough for the given email and whether or not it addresses all the points 
         mentioned in the email. You only have to give a 'yes' or a 'no' as response and nothing else. 'yes' means that the reply is good enough and that 
         it can be considered as the final reply and 'no' means that the reply is not good enough and it should be rewritten."""),
        ("human", """Analyse the given email and the generated reply:
          
         Email: {email}

         Reply: {reply}""")
    ]
)

reply = ""

def check_reply(result):
    return result

marketing_social_chain = marketing_social_email_node | model | StrOutputParser()

def marketing_social_branch(result):
    global email
    global reply
    if "yes" in result.lower():
        reply = marketing_social_chain.invoke({"email" : email})
        return reply
    else:
        return reply

positive_feedback_chain = positive_feedback_node | model | StrOutputParser()

negative_feedback_chain = negative_feedback_node | model | StrOutputParser()

general_email_chain = general_email_node | model | StrOutputParser()

marketing_social_email_decision_chain = marketing_social_email_decision_node | model | StrOutputParser() | RunnableLambda(marketing_social_branch)

escalate_to_human_chain = escalate_to_human_node | model | StrOutputParser()

def classification_branch(result):
    global email
    global reply
    if "positive feedback" in result.lower():
        print("Positive Feedback\n")
        reply = positive_feedback_chain.invoke({"email" : email})
        return reply

    elif "negative feedback" in result.lower():
        print("Negative Feedback\n")
        reply = negative_feedback_chain.invoke({"email" : email})
        return reply
    
    elif "general email" in result.lower():
        print("General Email\n")
        reply = general_email_chain.invoke({"email" : email})
        return reply

    elif "marketing or social spam" in result.lower():
        print("Marketing or Social Spam\n")
        reply = marketing_social_email_decision_chain.invoke({"email" : email})
        return reply
    
    else:
        print("Escalate to Human\n")
        reply = escalate_to_human_chain.invoke({"email" : email})
        return reply

classification_chain = classification_node | model | StrOutputParser()

reply_generation_chain = classification_chain | RunnableLambda(classification_branch)

def content_check_branch(result):
    print("Inside Content Check Function")
    global email
    global reply
    if "yes" in result.lower():
        print("Content is perfect!")
        return reply
    else:
        print("Content Not Perfect...")
        reply = complete_chain()
        return reply

content_check_chain = content_check_node | model | StrOutputParser() | RunnableLambda(content_check_branch) | StrOutputParser()

def hallucination_check_branch(result):
    print("Inside Hallucination Function")
    global email
    global reply
    if reply != None and reply != "None":
        if "no" in result.lower():
            print("No Hallucination")
            reply = content_check_chain.invoke({"email" : email, "reply" : reply})
            return reply
        else:
            print("Hallucination Detected")
            reply = complete_chain()
            return reply

reply_checking_chain = halluciantion_check_node | model | StrOutputParser() | RunnableLambda(hallucination_check_branch) | StrOutputParser()

def complete_chain():
    global email
    global reply
    reply = reply_generation_chain.invoke({"email" : email})
    reply = reply_checking_chain.invoke({"email" : email, "reply" : reply})
    return reply

email1 = """Hi Ananya,
        I hope you're doing well. Just wanted to check in on you. I heard about your co-op offer, huge congratulations to you for that.
        Hope everyone in the family is fine. Let me know if you need any help.
        
        Best wishes
        Nabh"""

email2 = """Hello sir,
        We are from ElectroSteel Pvt Ltd, the following are this month's rates for wire rod:
        5 mm = ₹5500
        6 mm = ₹6500
        7 mm = ₹7500
        
        Let us know if you have any requirements."""

email3 = """Hello user,
        This is Team Instagram, Please find the summary of your earnings for this month. If you have any doubts, reach out to us at insta@insta.com"""

email4 = """Hello sir
        We recently got to know about your company and we would want to work with you, below is the list of services we provide:
        Tax Return Filing
        Bank Statement Analysis
        
        Please let us know if you would want any services from us."""

email = """Nabh, it's an emergency. Your grandfather has been admitted to the hospital and he's critical, the doctors are saying that he has very less 
        time left. I think you should come here and be with him."""

print(reply_checking_chain.invoke({"email" : email, "reply" : reply_generation_chain.invoke({"email" : email})}))