from django.urls import path
from .views import dashboard, policy_detail, like_policy, reshare_policy, add_policy, analyst_extract, chat_messages, post_chat_message, trendings, home

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('policy/<int:pk>/', policy_detail, name='policy_detail'),
    path('policy/<int:pk>/like/', like_policy, name='like_policy'),
    path('policy/<int:pk>/reshare/', reshare_policy, name='reshare_policy'),
    path('add_policy/', add_policy, name='add_policy'),
    path('policy/<int:pk>/extract/', analyst_extract, name='analyst_extract'),
    path('chat/messages/', chat_messages, name='chat_messages'),
    path('chat/post/', post_chat_message, name='post_chat_message'),
    path('trendings/', trendings, name='trendings'),
    path('home/', home, name='home'),
]
