from django.urls import path

#
# Views
#
from .views import VideoUploadAPIView

urlpatterns = [
    path('', VideoUploadAPIView.as_view(), name='video_upload'),
]