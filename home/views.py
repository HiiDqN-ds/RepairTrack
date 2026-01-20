from django.shortcuts import render
from tickets.models import Ticket
from django.contrib.auth.models import User
from django.http import JsonResponse
import json

def index(request):
    return render(request, 'home/index.html')
