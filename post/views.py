from django.db import IntegrityError
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, get_object_or_404
from rest_framework.authentication import SessionAuthentication, TokenAuthentication


from .models import Tweet, Comment, LikeTweet, DislikeTweet
from .serializers import TweetSerializer, CommentSerializer
from .permissions import IsAuthorPermission
from .paginations import StandardPagination


class TweetViewSet(ModelViewSet):
    queryset = Tweet.objects.all()
    serializer_class = TweetSerializer
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthorPermission, ]
    pagination_class = StandardPagination

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        queryset = self.queryset
        print(self.request.query_params)
        user = self.request.query_params.get("user")
        if user:
            queryset = queryset.filter(user__username=user)
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(text__icontains=search)
        return queryset


class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthorPermission, ]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CommentListCreateAPIView(ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthorPermission, ]

    def get_queryset(self):

        return self.queryset.filter(tweet_id=self.kwargs['tweet_id'])

    def perform_create(self, serializer):
        serializer.save(user=self.request.user,
                        tweet=get_object_or_404(Tweet, id=self.kwargs['tweet_id']))


class CommentRetrieveDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthorPermission, ]


class PostTweetLike(APIView):
    def get(self, request, tweet_id):
        tweet = get_object_or_404(Tweet, id=tweet_id)
        try:
            like = LikeTweet.objects.create(tweet=tweet, user=request.user)
        except IntegrityError:
            like = LikeTweet.objects.filter(tweet=tweet, user=request.user).delete()
            data = {f"Лайк для {tweet_id} твита убрал пользователь {request.user.username}"}
            return Response(data, status=status.HTTP_403_FORBIDDEN)
        else:
            if DislikeTweet.objects.filter(tweet=tweet, user=request.user):
                dislike = DislikeTweet.objects.get(tweet=tweet, user=request.user).delete()
                data = {f"Был убран дизлайк с твита {tweet_id} и вместо неё поставлен лайк пользователем"
                        f" {request.user.username}"}
                return Response(data, status=status.HTTP_201_CREATED)
            data = {'message': f"лайк твиту {tweet_id} поставил пользователь {request.user.username}"}
            return Response(data, status=status.HTTP_201_CREATED)


class PostTweetDislike(APIView):
    def get(self, request, tweet_id):
        tweet = get_object_or_404(Tweet, id=tweet_id)
        try:
            dislike = DislikeTweet.objects.create(tweet=tweet, user=request.user)
        except IntegrityError:
            dislike = DislikeTweet.objects.filter(tweet=tweet, user=request.user).delete()
            data = {'Errors': f"дизлайк {tweet_id} был убран пользователем {request.user.username}"}
            return Response(data, status=status.HTTP_403_FORBIDDEN)
        else:
            if LikeTweet.objects.filter(tweet=tweet, user=request.user):
                like = LikeTweet.objects.get(tweet=tweet, user=request.user).delete()
                data = {f"Был убран лайк с твита {tweet_id} и вместо неё поставлен дизлайк пользователем"
                        f" {request.user.username}"}
                return Response(data, status=status.HTTP_201_CREATED)
            data = {f"дизлайк твиту {tweet_id} поставил пользователь {request.user.username}"}
            return Response(data, status=status.HTTP_201_CREATED)
