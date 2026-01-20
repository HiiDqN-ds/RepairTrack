from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from .models import Ticket

# tickets/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.core.mail import send_mail
from .models import Ticket

@csrf_exempt
def ticket_list(request):
    if request.method == "POST":
        try:
            name = request.POST.get("client_name")
            email = request.POST.get("client_email")
            phone = request.POST.get("client_phone")
            device_type = request.POST.get("device_type")
            device_model = request.POST.get("device_model")
            description = request.POST.get("problem_description")
            price = request.POST.get("estimated_price") or 0
            photo = request.FILES.get("device_photo")

            if not name or not email or not device_type:
                return JsonResponse({"error": "Missing required fields"}, status=400)

            # Create or get user
            user, created = User.objects.get_or_create(
                username=email,
                defaults={"email": email, "first_name": name}
            )

            ticket = Ticket.objects.create(
                title=f"{device_type} repair",
                description=description,
                client=user,
                client_phone=phone,
                device_type=device_type,
                device_model=device_model,
                estimated_price=price,
                device_photo=photo
            )

            # Send email to client
            subject = f"Reparaturauftrag erhalten – Tracking #{ticket.tracking_id}"
            message = f"""
Hallo {name},

Wir haben Ihren Reparaturauftrag erfolgreich erhalten!

Tracking-Nummer: {ticket.tracking_id}

Bitte senden Sie Ihr Gerät an folgende Adresse:

Tanitech Services
Friedrichstraße 1
40217 Düsseldorf
Deutschland

Sie können den Status Ihres Auftrags jederzeit mit der Tracking-Nummer verfolgen.

Vielen Dank für Ihr Vertrauen!
Ihr Tanitech Team
"""
            send_mail(
                subject,
                message,
                None,  # uses DEFAULT_FROM_EMAIL
                [email],
                fail_silently=False,
            )

            return JsonResponse({
                "success": True,
                "ticket_id": ticket.id,
                "tracking_id": ticket.tracking_id
            })

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid method"}, status=405)



@csrf_exempt
def ticket_detail(request, tracking_id):
    try:
        ticket = Ticket.objects.get(tracking_id=tracking_id)
        data = {
            "tracking_id": ticket.tracking_id,
            "title": ticket.title,
            "description": ticket.description,
            "status": ticket.status,
            "client": ticket.client.username,
            "device_type": ticket.device_type,
            "device_model": ticket.device_model,
            "estimated_price": float(ticket.estimated_price),
            "client_phone": ticket.client_phone,
            "created_at": ticket.created_at.strftime("%Y-%m-%d %H:%M"),
            "updated_at": ticket.updated_at.strftime("%Y-%m-%d %H:%M")
        }
        return JsonResponse(data)
    except Ticket.DoesNotExist:
        return JsonResponse({"error": "Ticket not found"}, status=404)
