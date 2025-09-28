from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", homePage, name="home_page"),
    
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path("register/", register_view, name="register"),
    path("logout/", logout_view, name="logout"),
    path("users/", user_list, name="user-list"),
    
    path("chat/start/<int:user_id>/", start_chat, name="chat-room-start"),
    path("chat/<str:room_uuid>/", chat_room, name="chat-room"),
    path('chat/message/<int:message_id>/delete/', delete_message, name='delete_message'),
    
    path("chat/<str:room_uuid>/upload/", upload_attachment, name="chat_upload"),
    path("chat/<str:room_uuid>/offer/", create_offer, name="chat_offer"),
    path("chat/<str:room_uuid>/offer/<int:message_id>/action/", offer_action, name="chat_offer_action"),
]