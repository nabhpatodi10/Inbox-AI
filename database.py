from pymongo import MongoClient
import os

class database():

    __client = None
    __collection = None

    def __init__(self):
        try:
            self.__client = MongoClient(os.getenv("MONGODB_URI"))
            self.__collection = self.__client["User-Information"]["Basic-Information"]
            print("Connection Successful")
        except Exception as error:
            print(error)
            return
    
    def insert(self, username: str, fullname: str, email: str, information: str, email_classes: str, send_mails: bool = True, mark_mails: bool = True) -> bool:
        try:
            if self.__collection.find_one({"username" : username}) is None:
                result = self.__collection.insert_one(
                    {
                        "username" : username,
                        "fullname" : fullname,
                        "email_id" : email,
                        "user_information" : information,
                        "email_classes" : email_classes,
                        "settings" : {
                            "send_mails_directly" : send_mails,
                            "mark_mails_read" : mark_mails
                        }
                    }
                )
                return result.acknowledged
            else:
                print("Username taken")
                return False
        except Exception as error:
            print(error)
            return False

    def update(self, username: str, data: dict) -> bool:
        try:
            query_filter = {"username" : username}
            values = {}
            for i in data:
                if i == "send_mails_directly":
                    values["settings.send_mails_directly"] = data[i]
                elif i == "mark_mails_read":
                    values["settings.mark_mails_read"] = data[i]
                else:
                    values[i] = data[i]
            update_operation = {"$set" : values}
            result = self.__collection.update_one(query_filter, update_operation)

            if result.acknowledged and result.modified_count == 1:
                print("Update Successful")
            else:
                print("Update Unsuccessful")
            return result.acknowledged
        except Exception as error:
            print(error)
            return False

    def delete(self, username: str) -> bool:
        try:
            query_filter = {"username" : username}
            result = self.__collection.delete_one(query_filter)

            if result.acknowledged and result.deleted_count == 1:
                print("Delete Successful")
            else:
                print("Delete Unsuccessful")
            return result.acknowledged
        except Exception as error:
            print(error)
            return False

    def get(self, username: str) -> dict | None:
        try:
            query_filter = {"username" : username}
            result = self.__collection.find_one(query_filter)

            if result is None:
                print("Data not found")
            else:
                return result
        except Exception as error:
            print(error)