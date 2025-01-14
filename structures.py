from pydantic import BaseModel, Field

class structures:

    class classification_output(BaseModel):

        email_class: str = Field(description="The class to which the email has been classified")

    class decision_output(BaseModel):

        decision: bool = Field(description="Boolean field to give the decision in True or False")

    class reply_output(BaseModel):

        reply: str = Field(description="The reply to the given email")

    class signup_input(BaseModel):

        username: str = Field(description="A unique username for the user to identify the account")
        fullname: str = Field(description="The Full Name of the user")
        email: str = Field(description="Email of the user")
        user_information: str = Field(description="Basic information about the user which shouls always be kept in mind while writing the emails")
        email_classes: str = Field(description="The classes in which the user wants to classify the emails")
        send_mails: bool = Field(description="Setting to turn on or off the send mail option or store as a draft", default=True)
        mark_mails: bool = Field(description="Setting to turn on or off the mark emails as read option", default=True)