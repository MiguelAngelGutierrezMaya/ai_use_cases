from django.urls import path

#
# Views
#
from .views import RtDetrAPIView, RfDetrAPIView

urlpatterns = [
    path('rt-detr', RtDetrAPIView.as_view(), name='rt_detr'),
    path('rf-detr', RfDetrAPIView.as_view(), name='rf_detr'),
]