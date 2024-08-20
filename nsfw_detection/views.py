#
# Python dependencies
#
import os
import uuid

#
# Django rest framework dependencies
#
from rest_framework.response import Response
from rest_framework.views import APIView

from nsfw_detection.modules.infrastructure.process_image import ProcessImage


# Create your views here.

#
# Nsfw image upload API view
#
class NsfwImageUploadAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    #
    # POST method
    #
    def post(self, request):
        image = request.FILES.get("image")

        #
        # Validate image exists
        #
        if not image:
            return Response({"message": "Image not found!"}, status=400)

        #
        # Validate image size under 20MB
        #
        if image.size > 20971520:
            return Response({"message": "Image size exceeds 20MB limit!"}, status=400)

        #
        # Validate image format is jpg or jpeg or png
        #
        if not image.name.endswith(".jpg") and not image.name.endswith(".jpeg") and not image.name.endswith(".png"):
            return Response({"message": "Image format must be jpg, png or jpeg!"}, status=400)

        random_name = uuid.uuid4()

        #
        # Change image name by uuid
        #
        image.name = f"{random_name}.jpg"

        #
        # Create folder if not exists
        #
        if not os.path.exists("files"):
            os.makedirs("files")

        image_root = "files/images"

        #
        # Create folder image if not exists
        #
        if not os.path.exists(image_root):
            os.makedirs(image_root)

        #
        # Create folder with random name if not exists
        #
        if not os.path.exists(f"{image_root}/{random_name}"):
            os.makedirs(f"{image_root}/{random_name}")

        #
        # Create and upload file
        #
        with open(f"{image_root}/{random_name}/{image.name}", "wb") as f:
            f.write(image.read())

        detection = ProcessImage(
            image_path=f"{image_root}/{random_name}/{image.name}"
        ).process(
        )

        return Response({
            "message": "Image uploaded and processed successfully!",
            "detection": detection
        }, status=200)
