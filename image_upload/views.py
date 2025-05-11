#
# Django rest framework dependencies
#
from rest_framework.views import APIView
from rest_framework.response import Response

#
# Image upload module
#
from .modules.infrastructure.upload_image import upload_image
from .modules.infrastructure.process_image_rfdetr import ProcessImageRfdetr
# Create your views here.

class ImageUploadAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        #
        # Get image from request
        #
        image = request.FILES.get("image")

        #
        # Upload image
        #
        success, message, uploaded_image = upload_image(image)

        if not success:
            return Response({"message": message}, status=400)

        ProcessImageRfdetr(
            image_path=f"{uploaded_image['image_path']}",
            output_path=f"{uploaded_image['image_root']}/{uploaded_image['random_name']}/{image.name}-output.jpg"
        ).process()

        #
        # Return response
        #
        return Response({"message": message}, status=200)
