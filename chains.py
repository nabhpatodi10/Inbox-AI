from langchain_groq import ChatGroq

from nodes import mail_nodes, thread_nodes
from structures import structures

class mail_chains():

    __mail_node = mail_nodes()
    __structure = structures()
    __model = ChatGroq(model = "llama-3.3-70b-versatile")

    reply_decision_chain = __mail_node.reply_decision_node | __model.with_structured_output(__structure.decision_output)

    classification_chain = __mail_node.classification_node | __model.with_structured_output(__structure.classification_output)

    reply_writing_chain = __mail_node.reply_writing_node | __model.with_structured_output(__structure.reply_output)

    hallucination_check_chain = __mail_node.hallucination_check_node | __model.with_structured_output(__structure.decision_output)

    content_check_chain = __mail_node.content_check_node | __model.with_structured_output(__structure.decision_output)

class thread_chains():

    __thread_node = thread_nodes()
    __structure = structures()
    __model = ChatGroq(model = "llama-3.3-70b-versatile")

    reply_decision_chain = __thread_node.reply_decision_node | __model.with_structured_output(__structure.decision_output)

    classification_chain = __thread_node.classification_node | __model.with_structured_output(__structure.classification_output)

    reply_writing_chain = __thread_node.reply_writing_node | __model.with_structured_output(__structure.reply_output)

    hallucination_check_chain = __thread_node.hallucination_check_node | __model.with_structured_output(__structure.decision_output)

    content_check_chain = __thread_node.content_check_node | __model.with_structured_output(__structure.decision_output)