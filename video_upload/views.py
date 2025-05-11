#
# Python dependencies
#
import os
import uuid

from .modules.infrastructure.process_video_rtdert import ProcessVideo as ProcessVideoRtDetr
from .modules.infrastructure.upload_video import upload_video
#
# Django rest framework dependencies
#
from rest_framework.response import Response
from rest_framework.views import APIView


# Create your views here.

#
# Video upload API view
#
class RtDetrAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    #
    # POST method
    #
    def post(self, request):
        video = request.FILES.get("video")

        success, message, uploaded_video = upload_video(video)

        if not success:
            return Response({"message": message}, status=400)


        ProcessVideoRtDetr(
            video_path=f"{uploaded_video['video_path']}",
            output_path=f"{uploaded_video['video_root']}/{uploaded_video['random_name']}/{video.name}-output.mp4"
        ).process()

        return Response({"message": "Video uploaded and processed successfully!"}, status=200)
