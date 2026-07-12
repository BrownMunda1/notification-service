import time
import logging

from django.http import HttpResponseNotAllowed

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated

from api.serializers import NotificationSerializer
from api.tasks import send_notification_task

@api_view(["POST"])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def notify(request: Request):

    start_time = time.time()

    if request.method != "POST":
        return HttpResponseNotAllowed(permitted_methods=["POST"])

    serializer = NotificationSerializer(data=request.data)
    try:
        if serializer.is_valid():
            serializer.save()
            send_notification_task.delay(serializer.data["id"])
            return Response({"id": serializer.data["id"], "status": "queued"}, status=status.HTTP_202_ACCEPTED)
        print("Error while sending notification: Request Body invalid")
        return Response(data={"message": "Invalid Request Body", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(f"Exception while sending notification: {e}")
        logging.exception("Exception while sending notification")
        return Response(data={"error_message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
