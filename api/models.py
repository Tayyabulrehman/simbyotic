from uuid import uuid4

from django.db import models

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import os
from dotenv import load_dotenv


# # Create your models here.
# class Contact(models.Model):
#     first_name = models.CharField(
#         db_column="FirstName", default=None, null=True, max_length=255
#     )
#     last_name = models.CharField(
#         db_column="LastName", default=None, null=True, max_length=255
#     )
#     email = models.EmailField(db_column="Email", default=None, null=True, unique=False)
#     # company_name = models.CharField(db_column="CompanyName", default=None, null=True, max_length=255)
#
#     message = models.TextField(db_column="Message", default=None, null=True)
#     meeting_date = models.DateField(db_column="MeetingDate", default=None, null=True)
#     meeting_time = models.TimeField(db_column="MeetingTime", default=None, null=True)
#     # status = models.CharField(db_column="Status", default=BusinessRequestStatus.PENDING, null=True, max_length=255)
#     response_comment = models.TextField(
#         db_column="ResponseComment", default=None, null=True
#     )
#
#     meeting_link = models.URLField(db_column="MeetingLink", null=True)
#     timezone = models.CharField(db_column="TimeZone", null=True, max_length=255)
#
#     class Meta:
#         db_table = "Contact-us"


def schedule_meeting(title, description, start, end, attendees, zone):
        SCOPES = ["https://www.googleapis.com/auth/calendar"]

        creds = Credentials.from_authorized_user_info(
            info={
                "refresh_token": os.getenv("GOOGLE_REFRESH_TOKEN"),
                "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                "client_secret": os.getenv('GOOGLE_CLIENT_SECRETE'),
            },
            scopes=SCOPES,
        )

        try:
            service = build("calendar", "v3", credentials=creds)

            event = {
                "summary": title,
                "description": description,
                "start": {"dateTime": start, "timeZone": zone},
                "end": {"dateTime": end, "timeZone": zone},
                "conferenceData": {
                    "createRequest": {
                        "requestId": f"{uuid4().hex}",
                        "conferenceSolutionKey": {"type": "hangoutsMeet"},
                    }
                },
                "attendees": attendees,
            }

            event = (
                service.events()
                    .insert(
                    calendarId="primary",
                    body=event,
                    conferenceDataVersion=1,
                    sendNotifications=True,
                )
                    .execute()
            )
            return event.get("hangoutLink")
            # print(f'Event created: {event.get("htmlLink")}')

        except Exception as e:
            print(e)
            return