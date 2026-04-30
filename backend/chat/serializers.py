from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Room, Message


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('id', 'email', 'name')


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ('id', 'room', 'sender', 'content', 'timestamp', 'is_read')
        read_only_fields = ('id', 'sender', 'timestamp')


class RoomSerializer(serializers.ModelSerializer):
    members = UserSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = (
            'id', 'name', 'description', 'members',
            'last_message', 'unread_count', 'is_private', 'created_at'
        )

    def get_last_message(self, obj):
        msg = obj.messages.last()
        if msg:
            return {
                'content': msg.content,
                'timestamp': msg.timestamp.isoformat()
            }
        return None

    def get_unread_count(self, obj):
        user = self.context['request'].user
        return obj.messages.filter(
            is_read=False
        ).exclude(sender=user).count()