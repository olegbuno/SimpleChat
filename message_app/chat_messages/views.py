from django.contrib.auth.models import User
from django.db.models import Count
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.response import Response

from .models import Thread, Message
from .serializers import ThreadSerializer, MessageSerializer


class ThreadViewSet(viewsets.ModelViewSet):
    queryset = Thread.objects.all()
    serializer_class = ThreadSerializer

    def create(self, request, *args, **kwargs):
        participants = list(map(int, request.data.getlist('participants', [])))
        if len(participants) > 2:
            raise ValidationError('A thread can\'t have more than 2 participants.')

        # Check if a thread already exists with the same participants
        existing_threads = Thread.objects.annotate(num_participants=Count('participants')).filter(
            num_participants=len(participants)
        )
        for thread in existing_threads:
            thread_participants = list(thread.participants.values_list('id', flat=True))
            if participants == thread_participants:
                serializer = self.get_serializer(thread)
                return Response(serializer.data, status=status.HTTP_200_OK)

        thread_serializer = self.get_serializer(data=request.data)
        thread_serializer.is_valid(raise_exception=True)
        thread = thread_serializer.save()

        # Add participants to the thread
        thread.participants.add(*participants)

        return Response(thread_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def user_threads(self, request):
        user = self.request.user
        threads = Thread.objects.filter(participants=user)
        serializer = self.get_serializer(threads, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def create_message(self, request, pk=None):
        thread = self.get_object()
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(sender=request.user, thread=thread)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'])
    def mark_as_read(self, request, pk=None):
        message_id = request.data.get('id')
        if message_id is None:
            return Response({'error': 'Message ID not provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            message = Message.objects.get(pk=message_id)
        except Message.DoesNotExist:
            raise NotFound('Message not found')

        message.is_read = True
        message.save()
        return Response(status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        # Check if the authenticated user is a participant of the thread
        if request.user not in instance.participants.all():
            return Response({'error': 'You are not a participant of this thread'},
                            status=status.HTTP_403_FORBIDDEN)

        # If the user is a participant, delete the thread
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def unread_messages_count(self, request):
        user_id = request.query_params.get('user_id')
        print('user_id:', user_id)
        if user_id is None:
            return Response({'error': 'User ID not provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        unread_count = Message.objects.filter(thread__participants=user, is_read=False).count()
        return Response({'unread_count': unread_count})


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, thread_id=request.data.get('thread'))
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        thread_id = self.request.query_params.get('thread_id')
        if thread_id:
            return Message.objects.filter(thread_id=thread_id)
        return Message.objects.all()
