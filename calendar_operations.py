from googleapiclient.discovery import build
import datetime
from zoneinfo import ZoneInfo

from authorisation import authorisation

class calendar_operations():

    __creds = None
    __service = None

    def __init__(self):
        auth = authorisation()
        self.__creds = auth.cred_token_auth()
        self.__service = build("calendar", "v3", credentials = self.__creds)

    def __del__(self):
        self.__service.close()

    def get_calendar_list(self) -> dict:
        try:
            calendars = {}
            page_token = None
            while True:
                calendar_list = self.__service.calendarList().list(pageToken = page_token).execute()
                for calendar in calendar_list["items"]:
                    calendars[calendar["id"]] = {"summary" : calendar["summary"], "timeZone" : calendar["timeZone"]}
                page_token = calendar_list.get("nextPageToken")
                if not page_token:
                    break
            print(calendars)
            return calendars
        except Exception as error:
            raise error

    def get_events_from_calender(self, id: str, timezone: str, num_days: int) -> dict:
        try:
            events = {}
            now = datetime.datetime.now(tz = ZoneInfo(timezone))
            event_list = self.__service.events().list(calendar_id = id, Timemin = now, Timemax = now + datetime.timedelta(days = num_days), orderby = "startTime").execute()
            event_list = event_list.get("items", [])
            for event in event_list:
                events[event["id"]] = {"status" : event["status"], "summary" : event["summary"], "description" : event["description"], "location" : event["location"], "start" : event["start"], "end" : event["end"], "eventType" : event["eventType"]}
            return events
        except Exception as error:
            raise error
        
    def get_all_events(self, calendars: dict, num_days: int) -> dict:
        try:
            events = {}
            for calendar in calendars:
                events[calendar] = self.get_events_from_calender(calendar, calendar["timeZone"], num_days)
            return events
        except Exception as error:
            raise error
        
    def quick_add_event(self, text: str, calendar_id: str = "primary") -> bool:
        try:
            event = None
            event = self.__service.events().quickAdd(calendarId = calendar_id, text = text).execute()
            if event:
                return True
            else:
                return False
        except Exception as error:
            raise error
        
    def create_event(self, summary: str, location: str, description: str, start: dict, end: dict, recurrence: list, attendees: list, reminders: dict, calendar_id: str = "primary") -> bool:
        try:
            final_event = None
            event = {
                "summary" : summary,
                "location" : location,
                "description" : description,
                "start" : start,
                "end" : end,
                "recurrence" : recurrence,
                "attendees" : attendees,
                "reminders" : reminders
            }

            final_event = self.__service.events().insert(calenderId = calendar_id, body = event).execute()

            if final_event:
                return True
            else:
                return False
        except Exception as error:
            raise error
        
    def update_event(self, event_id, changes : dict, calendar_id : str = "primary"):
        try:
            update = None
            event = self.__service.events().get(calendarId = calendar_id, eventId = event_id).execute()
            for i in changes:
                event[i] = changes[i]
            update = self.__service.events().update(calendarId = calendar_id, eventId = event_id, body = event).execute()
            if update:
                return True
            else:
                return False
        except Exception as error:
            raise error
        
    def events_in_range(self, calendars: dict, start_time: datetime.datetime, weeks: int = 0, days: int = 0, hours: int = 0, mins: int = 0) -> dict:
        try:
            events = {}
            for calendar in calendars:
                cal_events = {}
                event_list = self.__service.events().list(calendar_id = id, Timemin = start_time, Timemax = start_time + datetime.timedelta(weeks = weeks, days = days, hours = hours, minutes = mins), orderby = "startTime").execute()
                event_list = event_list.get("items", [])
                if len(event_list) > 0:
                    for event in event_list:
                        cal_events[event["id"]] = {"status" : event["status"], "summary" : event["summary"], "description" : event["description"], "location" : event["location"], "start" : event["start"], "end" : event["end"], "eventType" : event["eventType"]}
                    events[calendar] = cal_events
            return events
        except Exception as error:
            raise error