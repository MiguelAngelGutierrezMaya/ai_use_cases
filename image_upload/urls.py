from django.urls import path

#
# Views
#
from .views import ImageUploadAPIView

urlpatterns = [
    path('', ImageUploadAPIView.as_view(), name='image_upload'),
]