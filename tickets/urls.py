from django.urls import path
from .views import ticket_list, ticket_detail

urlpatterns = [
    path('tickets/', ticket_list, name='ticket_list'),
    path('tickets/<str:tracking_id>/', ticket_detail, name='ticket_detail'),
]
