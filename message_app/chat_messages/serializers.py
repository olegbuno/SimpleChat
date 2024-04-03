from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Thread, Message


class ThreadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thread
        fields = '__all__'


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'sender', 'text', 'thread']

    def __init__(self, *args, **kwargs):
        thread_id = kwargs.pop('thread_id', None)
        super().__init__(*args, **kwargs)
        if thread_id is not None:
            self.fields['sender'].queryset = User.objects.filter(thread__id=thread_id)
