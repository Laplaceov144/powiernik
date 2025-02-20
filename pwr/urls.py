from django.urls import path
from . import views

urlpatterns = [
    path('send/', views.send_message, name='send_message'),
    path('receive/<uuid:message_id>/', views.receive_message, name='receive_message'),
    path('bulk-action/', views.bulk_action, name='bulk_action')
]
