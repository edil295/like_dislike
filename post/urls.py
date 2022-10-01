from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views


router = DefaultRouter()
router.register('tweet', views.TweetViewSet, basename='tweet')
router.register('comment', views.CommentViewSet, basename='comment')

urlpatterns = [
    path('', include(router.urls)),
    path('tweet/<int:tweet_id>/comment/', views.CommentListCreateAPIView.as_view()),
    path('tweet/<int:tweet_id>/comment/<int:pk>/', views.CommentRetrieveDestroyAPIView.as_view()),
    path('tweet/<int:tweet_id>/like/', views.PostTweetLike.as_view()),
    path('tweet/<int:tweet_id>/dislike/', views.PostTweetDislike.as_view()),

]
