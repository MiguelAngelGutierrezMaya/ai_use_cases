from django.urls import path

#
# Views
#
from .views import NsfwImageUploadAPIView

urlpatterns = [
    path('', NsfwImageUploadAPIView.as_view(), name='nsfw_image_upload'),
]
