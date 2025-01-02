from pydantic import BaseModel, Field

class structures:

    class classification_output(BaseModel):

        email_class: str = Field(description="The class to which the email has been classified")

    class decision_output(BaseModel):

        decision: bool = Field(description="Boolean field to give the decision in True or False")

    class reply_output(BaseModel):

        reply: str = Field(description="The reply to the given email")