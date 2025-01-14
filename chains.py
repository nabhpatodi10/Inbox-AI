from langchain_groq import ChatGroq
from langchain.schema.runnable import RunnableLambda

from nodes import mail_nodes, thread_nodes
from structures import structures

class chain_functions():

    __user: str = ""
    __information: str = ""
    __email_classes: str = ""
    __email: str = ""
    __mails: list = []
    __node_type: thread_nodes | mail_nodes = thread_nodes()
    __structure = structures()
    __model = ChatGroq(model = "llama-3.3-70b-versatile")

    __reply_decision_chain = __node_type.reply_decision_node | __model.with_structured_output(__structure.decision_output)

    __classification_chain = __node_type.classification_node | __model.with_structured_output(__structure.classification_output)

    __reply_writing_chain = __node_type.reply_writing_node | __model.with_structured_output(__structure.reply_output)

    __hallucination_check_chain = __node_type.hallucination_check_node | __model.with_structured_output(__structure.decision_output)

    __content_check_chain = __node_type.content_check_node | __model.with_structured_output(__structure.decision_output)

    __final_chain = None

    def __init__(self, user: str, information: str, email_classes: str, mails: list):
        self.__user = user
        self.__information = information
        self.__email_classes = email_classes
        self.__mails = mails

        self.__final_chain = self.__reply_decision_chain | RunnableLambda(lambda x: self.__email_classification(x)) | RunnableLambda(lambda x: self.__reply_writing(x)) | RunnableLambda(lambda x: self.__hallucination_check(x)) | RunnableLambda(lambda x: self.__content_check(x)) | RunnableLambda(lambda x: self.__chain_end(x))

    def __email_classification(self, decision):
        if decision.decision == True:
            return self.__classification_chain.invoke({"user" : self.__user, "information" : self.__information, "email_classes" : self.__email_classes, "email" : self.__email})
        else:
            return "No Reply Required"
        
    def __reply_writing(self, email_class):
        print("In Writing Node", end = "\n")
        if email_class == "No Reply Required":
            return email_class
        elif "escalate to human" in email_class.email_class.lower():
            return "Escalate to Human"
        else:
            print("Writing Reply", end = "\n")
            return self.__reply_writing_chain.invoke({"email_class" : email_class.email_class, "user" : self.__user, "information" : self.__information, "email" : self.__email})
        
    def __hallucination_check(self, reply):
        print("In Hallucination Check Node", end = "\n")
        if isinstance(reply, str):
            return reply
        else:
            print("Checking Hallucination", end = "\n")
            return {"decision" : self.__hallucination_check_chain.invoke({"email" : self.__email, "reply" : reply.reply}), "reply" : reply}
        
    def __content_check(self, decision):
        print("In Content Check Node", end = "\n")
        if isinstance(decision, str):
            return decision
        elif decision["decision"].decision == True:
            print("Hallucination Found", end = "\n")
            return self.__content_chain_call()
        else:
            print("Checking checking content", end = "\n")
            return {"decision" : self.__content_check_chain.invoke({"user" : self.__user, "information" : self.__information, "email" : self.__email, "reply" : decision["reply"].reply}), "reply" : decision["reply"]}
        
    def __chain_end(self, decision):
        print("Ending Chain", end = "\n")
        if isinstance(decision, str):
            return decision
        elif decision["decision"].decision == False:
            return self.final_output()
        else:
            return decision["reply"].reply

    def final_output(self) -> list | None:
        replies = []
        try:
            j = 1
            for mail in self.__mails:
                if mail["Type"] == "Single Mail":
                    self.__node_type = mail_nodes()
                elif mail["Type"] == "Thread":
                    self.__node_type = thread_nodes()
                print(f"Thread {j}: \n")
                self.__email = "Sender: " + mail["Sender"] + "\nSubject: " + mail["Subject"] + "\nEmail Body:"
                for i in mail["Body"]:
                    self.__email += i + "\n\n"
                print(self.__email, end = "\n")
                if "<" in mail["Sender"] and ">" in mail["Sender"]:
                    start = mail["Sender"].index("<")
                    sender_mail = mail["Sender"][start + 1 : -1]
                reply = self.__final_chain.invoke({"user" : self.__user, "information" : self.__information, "email" : self.__email})
                replies.append({"ID": mail["ID"], "Sender" : sender_mail, "Subject" : mail["Subject"], "Reply" : reply})
                j+=1
            return replies
        except Exception as e:
            print(e)
    
    def __content_chain_call(self):
        chain = self.__reply_decision_chain | RunnableLambda(lambda x: self.__email_classification(x)) | RunnableLambda(lambda x: self.__reply_writing(x)) | RunnableLambda(lambda x: self.__hallucination_check(x)) | RunnableLambda(lambda x: self.__content_check(x))
        return chain.invoke({"user" : self.__user, "information" : self.__information, "email" : self.__email})