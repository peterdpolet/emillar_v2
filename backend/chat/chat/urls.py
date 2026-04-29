from django.urls import path
from . import views

urlpatterns = [
    path('rooms/', views.RoomListView.as_view()),
    path('rooms/<str:room_name>/', views.RoomDetailView.as_view()),
    path('rooms/<str:room_name>/join/', views.join_room),
    path('rooms/<str:room_name>/messages/', views.MessageListView.as_view()),
]