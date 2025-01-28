from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.VideoUploadView.as_view(), name='video-upload'),
    path('<int:video_id>/trim/', views.VideoTrimView.as_view(), name='video-trim'),
    path('merge/', views.VideoMergeView.as_view(), name='video-merge'),
    path('<int:video_id>/share/', views.ShareLinkView.as_view(), name='video-share'),
    path('', views.VideoListView.as_view(), name='video-list'),
    path('<int:pk>/', views.VideoDetailView.as_view(), name='video-detail'),
]
