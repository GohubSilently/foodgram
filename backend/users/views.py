from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status, views, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import UserAvatarSerializer, UserSubscriptionSerializer
from .models import Subscription


CustomUser = get_user_model()


class CustomUserAvatarView(views.APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request):
        user = request.user
        serializer = UserAvatarSerializer(
            user, data=request.data, partial=True, context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        user = request.user
        if user.avatar:
            user.avatar.delete(save=True)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_404_NOT_FOUND)


class CustomUserSubscription(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk=None):
        user = request.user
        follower = get_object_or_404(CustomUser, pk=pk)

        if user == follower:
            return Response(
                {'detail': 'You cannot subscribe to yourself.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if Subscription.objects.filter(user=user, follower=follower).exists():
            return Response(
                {'detail': 'Already subscribed.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        Subscription.objects.create(user=user, follower=follower)

        serializer = UserSubscriptionSerializer(
            follower,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk=None):
        user = request.user
        follower = get_object_or_404(CustomUser, pk=pk)

        if user == follower:
            return Response(
                {'detail': 'You cannot unsubscribe from yourself.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        subscription = Subscription.objects.filter(
            user=user, follower=follower
        )
        if not subscription.exists():
            return Response(
                {'detail': 'Not subscribed.'},
                status=status.HTTP_404_NOT_FOUND
            )

        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscriptionsListView(generics.ListAPIView):
    serializer_class = UserSubscriptionSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return CustomUser.objects.filter(followers__user=self.request.user)
