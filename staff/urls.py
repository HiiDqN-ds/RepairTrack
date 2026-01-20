from django.urls import path
from . import views

app_name = 'staff'

urlpatterns = [
    path('login/', views.staff_login, name='login'),
    path('logout/', views.staff_logout, name='logout'),
    path('dashboard/', views.staff_dashboard, name='dashboard'),
    path('ticket/<int:id>/', views.staff_ticket_detail, name='staff_ticket_detail'),
    path('ticket/<int:id>/update/', views.update_ticket_status, name='update_ticket_status'),
    path('ticket/<int:id>/print/', views.print_ticket, name='print_ticket'),  # <--- new
]
