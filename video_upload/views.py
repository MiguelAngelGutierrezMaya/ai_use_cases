#
# Python dependencies
#
import os
import uuid

from .modules.infrastructure.process_video import ProcessVideo

#
# Django rest framework dependencies
#
from rest_framework.response import Response
from rest_framework.views import APIView


# Create your views here.

#
# Video upload API view
#
class VideoUploadAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    #
    # POST method
    #
    def post(self, request):
        video = request.FILES.get("video")

        #
        # Validate video exists
        #
        if not video:
            return Response({"message": "Video not found!"}, status=400)

        #
        # Validate video size under 20MB
        #
        if video.size > 20971520:
            return Response({"message": "Video size exceeds 20MB limit!"}, status=400)

        #
        # Validate video format is mp4
        #
        if not video.name.endswith(".mp4"):
            return Response({"message": "Video format must be mp4!"}, status=400)

        random_name = uuid.uuid4()

        #
        # Change video name by uuid
        #
        video.name = f"{random_name}.mp4"

        #
        # Create folder if not exists
        #
        if not os.path.exists("files"):
            os.makedirs("files")

        #
        # Create folder with random name if not exists
        #
        if not os.path.exists(f"files/{random_name}"):
            os.makedirs(f"files/{random_name}")

        #
        # Create and upload file
        #
        with open(f"files/{random_name}/{video.name}", "wb+") as destination:
            for chunk in video.chunks():
                destination.write(chunk)

        ProcessVideo(
            video_path=f"files/{random_name}/{video.name}",
            output_path=f"files/{random_name}/{random_name}-output.mp4"
        ).process()

        return Response({"message": "Video uploaded and processed successfully!"}, status=200)
