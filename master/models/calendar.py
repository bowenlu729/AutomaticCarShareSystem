from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from models import webdata


API_SERVICE_NAME = "calendar"
API_VERSION = "v3"
CALENDAR_ID = "primary"


def composeEventId(member, reservation):
    '''Compose a unique event id for Google Calendar.

    Parameters
    ----------
    member: dict
        Member dict collected via RESTful API.
    reservation: dict
        Reservation dict collected via RESTful API.

    Returns
    -------
    str
        A unique event id.
    '''

    reservedTimestamp = int(datetime.timestamp(reservation["reservedTime"]))
    eventId = "piotcss2755m%dr%dt%d" % (member["id"], reservation["id"], reservedTimestamp)
    return eventId


def insertEvent(credentials, member, car, reservation):
    '''Insert an event to member's Google Calendar.

    Parameters
    ----------
    credentials : Credentials
        Credentials acquired via OAuth process.
    member : dict
        Member dict collected via RESTful API.
    car : dict
        Car dict collected via RESTful API.
    reservation :dict
        Reservation dict collected via RESTful API.
    '''

    eventId = composeEventId(member, reservation)
    startTime = reservation["reservedTime"]
    endTime = startTime + timedelta(hours=reservation["reservedHours"])
    order = "Member ID: %s (%s)\n" % (member["username"], member["email"]) + \
            "Name: %s %s\n" % (member["firstName"], member["lastName"]) + \
            "Order No: R%06d\n" % (reservation["id"],) + \
            "Car: C%(id)04d / %(make)s / %(bodyType)s / %(colour)s / %(seats)d seats\n" % (car) + \
            "Location: %s\n" % (car["location"],) + \
            "Reserved Time: %s\n" % (webdata.datetimeToStr(webdata.convertUtcToLocal(startTime)),) + \
            "Duration: %d hours\n" % (reservation["reservedHours"],) + \
            "Total Cost: $%.2f" % (reservation["totalCost"],)
    body = {
        "id": eventId,
        "summary": "PIoTCSS - Car Reservation",
        "description": order,
        "location": car["location"],
        "start": {
            "dateTime": startTime.isoformat(),
            "timeZone": "UTC"
        },
        "end": {
            "dateTime": endTime.isoformat(),
            "timeZone": "UTC"
        }
    }

    try:
        service = build(API_SERVICE_NAME, API_VERSION, credentials=Credentials(**credentials))
        event = service.events().insert(calendarId=CALENDAR_ID, body=body).execute()
    except Exception as e:
        print(e)


def deleteEvent(credentials, member, reservation):
    '''Delete the event from member's Google Calendar

    Parameters
    ----------
    credentials : Credentials
        Credentials acquired via OAuth process.
    member : dict
        Member dict collected via RESTful API.
    reservation :dict
        Reservation dict collected via RESTful API.
    '''

    eventId = composeEventId(member, reservation)

    try:
        service = build(API_SERVICE_NAME, API_VERSION, credentials=Credentials(**credentials))
        event = service.events().delete(calendarId=CALENDAR_ID, eventId=eventId).execute()
    except Exception as e:
        print(e)
