from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Room, Message
from .serializers import RoomSerializer, MessageSerializer


class RoomListView(generics.ListAPIView):
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Room.objects.filter(
            members=self.request.user
        ).prefetch_related('members', 'messages')

    def get_serializer_context(self):
        return {'request': self.request}


class RoomDetailView(generics.RetrieveAPIView):
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'name'

    def get_queryset(self):
        return Room.objects.filter(members=self.request.user)

    def get_serializer_context(self):
        return {'request': self.request}


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def join_room(request, room_name):
    try:
        room = Room.objects.get(name=room_name)
        if room.is_private:
            return Response(
                {'detail': 'Room is private.'},
                status=status.HTTP_403_FORBIDDEN
            )
        room.members.add(request.user)
        return Response({'detail': 'Joined successfully.'})
    except Room.DoesNotExist:
        return Response(
            {'detail': 'Room not found.'},
            status=status.HTTP_404_NOT_FOUND
        )


class MessageListView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        room_name = self.kwargs['room_name']
        # Filter and order FIRST, slice LAST
        return Message.objects.filter(
            room__name=room_name,
            room__members=self.request.user
        ).select_related('sender').order_by('-timestamp')[:100]

    def list(self, request, *args, **kwargs):
        # Get queryset WITHOUT the slice for the update
        room_name = self.kwargs['room_name']
        base_qs = Message.objects.filter(
            room__name=room_name,
            room__members=self.request.user
        ).select_related('sender').order_by('-timestamp')

        # Mark as read BEFORE slicing
        base_qs.exclude(sender=request.user).update(is_read=True)

        # NOW slice for the response
        messages = list(base_qs[:100])
        messages.reverse()

        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)