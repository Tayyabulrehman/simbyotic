from django.conf import settings
from django.shortcuts import render

# Create your views here.
from rest_framework import renderers, status
from rest_framework.response import Response
from rest_framework.status import is_server_error
from rest_framework.views import APIView
import datetime as dt
from rest_framework import serializers

from api.models import schedule_meeting


class BaseAPIView(APIView):
    """
    Base class for API views.
    """

    authentication_classes = ()
    permission_classes = ()
    renderer_classes = [renderers.JSONRenderer]

    # throttle_classes = [AnonRateThrottle,UserRateThrottle]

    def send_response(
            self,
            success=False,
            code="",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            payload={},
            description="",
            exception=None,
            count=0,
            log_description="",
    ):
        """
        Generates response.
        :param success: bool tells if call is successful or not.
        :param code: str status code.
        :param status_code: int HTTP status code.
        :param payload: list data generated for respective API call.
        :param description: str description.
        :param exception: str description.
        :rtype: dict.
        """
        if not success and is_server_error(status_code):
            if settings.DEBUG:
                description = f"error message: {description}"
            else:
                description = "Internal server error."
        return Response(
            data={
                "success": success,
                "code": code,
                "payload": payload,
                "description": description,
                "exception": exception,
                "count": count,
            },
            status=status_code,
        )

    def send_data_response(
            self,
            success=False,
            code="",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            payload={},
            description="",
    ):
        """
        Generates response for data tables.
        :param success: bool tells if call is successful or not.
        :param code: str status code.
        :param status_code: int HTTP status code.
        :param payload: list data generated for respective API call.
        :param description: str description.
        :rtype: dict.
        """
        if not success and is_server_error(status_code):
            if settings.DEBUG:
                description = f"error message: {description}"
            else:
                description = "Internal server error."
        return Response(
            data={
                "data": {
                    "success": success,
                    "code": code,
                    "payload": payload,
                    "description": description,
                }
            },
            status=status_code,
        )

    # @staticmethod
    # def get_oauth_token(email="", password="", grant_type="password"):
    #     try:
    #         url = settings.AUTHORIZATION_SERVER_URL
    #         # url ='http://192.168.100.10:8000/api/oauth/token/'
    #         headers = {"Content-Type": "application/x-www-form-urlencoded"}
    #         data = {
    #             "username": email.lower(),
    #             "password": password,
    #             "grant_type": grant_type,
    #         }
    #         auth = HTTPBasicAuth(settings.OAUTH_CLIENT_ID, settings.OAUTH_CLIENT_SECRET)
    #         response = requests.post(url=url, headers=headers, data=data, auth=auth)
    #         if response.ok:
    #             json_response = response.json()
    #             return {
    #                 "access_token": json_response.get("access_token", ""),
    #                 "refresh_token": json_response.get("refresh_token", ""),
    #             }
    #         if response.status_code == 400:
    #             return {"error": response.json()["error_description"]}
    #         else:
    #             return {"error": response.json().get("error")}
    #     except Exception as e:
    #         # fixme: Add logger to log this exception
    #         return {"exception": str(e)}
    #
    # @staticmethod
    # def revoke_oauth_token(token):
    #     try:
    #         url = settings.REVOKE_TOKEN_URL
    #         headers = {"Content-Type": "application/x-www-form-urlencoded"}
    #         data = {
    #             "token": token,
    #             "client_secret": settings.OAUTH_CLIENT_SECRET,
    #             "client_id": settings.OAUTH_CLIENT_ID,
    #         }
    #         response = requests.post(url=url, headers=headers, data=data)
    #         if response.ok:
    #             return True
    #         else:
    #             return False
    #     except Exception:
    #         # fixme: Add logger to log this exception
    #         return False
    #
    # def get_sorting_query(self, order, column):
    #     order = "-" if order == "desc" else ""
    #     return f"{order}{column}"


class BusinessDemoRequestPOSTAPIViews(BaseAPIView):
    class BusinessDemoRequestSerializer(serializers.Serializer):
        first_name = serializers.CharField()
        last_name = serializers.CharField()
        email = serializers.EmailField()
        title = serializers.CharField(write_only=True)
        message = serializers.CharField()
        meeting_date = serializers.DateField()
        meeting_time = serializers.TimeField()
        meeting_link = serializers.URLField(read_only=True)
        timezone = serializers.CharField(required=False, allow_null=True, allow_blank=True)

        # status = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        #
        # class Meta:
        #     model = Contact
        #     exclude = (
        #         "created_on",
        #         "modified_on",
        #         "created_by",
        #         "modified_by",
        #         # "is_email_marketing"
        #     )

    """
    API View for Login Super Admin and Admin
    """
    authentication_classes = ()
    permission_classes = ()

    # @method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=False))
    # @method_decorator(blacklist_ratelimited(dt.timedelta(minutes=30), block=True))
    def post(self, request, pk=None):
        try:
            serializer = self.BusinessDemoRequestSerializer(data=request.data)
            if serializer.is_valid():
                data = serializer.validated_data
                # serializer.save()
                start = dt.datetime.combine(
                    data["meeting_date"],
                    data["meeting_time"],
                )
                end = dt.datetime.combine(
                    data["meeting_date"],
                    data["meeting_time"],
                )
                # target_timezone = pytz.timezone(settings.TIMEZONE)
                # start = start.replace(tzinfo=target_timezone)
                # end = end.replace(tzinfo=target_timezone)

                # dt.datetime.combine(serializer.instance.meeting_date, serializer.instance.meeting_time)
                a = schedule_meeting(
                    start=start.isoformat(),
                    end=end.isoformat(),
                    title="Contact ",
                    description=serializer.instance.message,
                    zone=serializer.instance.timezone,
                    attendees=[{"email": serializer.instance.email}],
                )
                print(a)
                serializer.instance.meeting_link = a
                serializer.instance.save()
                # send email to superadmin

                # send main to business admin

                print(a)
                return self.send_response(
                    success=True,
                    code=f"201",
                    status_code=status.HTTP_201_CREATED,
                    payload=serializer.data,
                    description="Request Sent Successfully",
                )
            else:
                return self.send_response(
                    code=f"422",
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    description="Error",
                    exception=serializer.errors,
                )

        except Exception as e:
            if hasattr(e.__cause__, "pgcode") and e.__cause__.pgcode == "23505":
                return self.send_response(
                    code=f"422",
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    description="Company with this name already exist",
                )
            else:
                return self.send_response(code=f"500", description=e)
