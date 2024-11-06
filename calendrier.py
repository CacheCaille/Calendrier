import datetime
import os.path
from datetime import timedelta, timezone
from datetime import date 
from dateutil import tz

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


def main():
  """Shows basic usage of the Google Calendar API.
  Prints the start and name of the next 10 events on the user's calendar.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    service = build("calendar", "v3", credentials=creds)
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    # Call the Calendar API
    print("Getting the upcoming 10 events")
    today = date.today()
    start= today - timedelta(days=today.weekday())
    end = start + timedelta(days=6)
    startstr = str(start) + 'T00:00:00.000000Z'
    endstr = str(end) + 'T00:00:00.000000Z'
    events_result = (
        service.events()
        .list(
            calendarId="dja0q39dkd2jtm0lco1arcgnviv2sjfl@import.calendar.google.com",
            timeMin=startstr,
            timeMax=endstr,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])

    if not events:
      print("No upcoming events found.")
      return
    prevDay = ""
    # Prints the start and name of the next 10 events
    for event in events:
      start = event["start"].get("dateTime", event["start"].get("date"))
      utc = datetime.datetime.strptime(start.replace('T', ' ')[:-6], '%Y-%m-%d %H:%M:%S')
      day = utc.strftime('%A')
      if (prevDay != day):
        print(utc.strftime('%A'))     
      print(str(utc), event["summary"])
      prevDay = day
      

  except HttpError as error:
    print(f"An error occurred: {error}")


if __name__ == "__main__":
  main()