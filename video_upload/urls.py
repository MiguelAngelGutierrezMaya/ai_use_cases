from django.urls import path

#
# Views
#
from .views import RtDetrAPIView

urlpatterns = [
    path('', RtDetrAPIView.as_view(), name='rt_detr'),
]