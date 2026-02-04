from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404

from .models import Ticket
from .utils import generate_pdf


# -----------------------------
# CREATE TICKET + SEND EMAIL WITH PDF
# -----------------------------
@csrf_exempt
def ticket_list(request):
    if request.method == "POST":
        try:
            first_name = request.POST.get("client_first_name")
            last_name = request.POST.get("client_last_name")
            email = request.POST.get("client_email")
            phone = request.POST.get("client_phone")
            device_type = request.POST.get("device_type")
            device_model = request.POST.get("device_model")
            description = request.POST.get("problem_description")
            price = request.POST.get("estimated_price") or 0
            photo = request.FILES.get("device_photo")

            if not first_name or not last_name or not email or not device_type:
                return JsonResponse({"error": "Missing required fields"}, status=400)

            # Create / Get User
            user, created = User.objects.get_or_create(
                username=email,
                defaults={
                    "email": email,
                    "first_name": first_name,
                    "last_name": last_name
                }
            )

            # Create Ticket (tracking_id generated automatically by model)
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

            # Generate PDF from utils.py
            pdf_buffer = generate_pdf(ticket)

            # Send Email with PDF
            subject = f"Reparaturauftrag – Tracking #{ticket.tracking_id}"
            body = f"""
Hallo {first_name} {last_name},

Ihr Reparaturauftrag wurde erfolgreich erstellt.

Tracking Nummer: {ticket.tracking_id}

Im Anhang finden Sie Ihren Auftrag als PDF.

Vielen Dank!
Tanitech Team
"""

            email_msg = EmailMessage(subject, body, None, [email])
            email_msg.attach(
                f"auftrag_{ticket.tracking_id}.pdf",
                pdf_buffer.getvalue(),
                "application/pdf"
            )
            email_msg.send(fail_silently=False)

            return JsonResponse({
                "success": True,
                "ticket_id": ticket.id,
                "tracking_id": ticket.tracking_id
            })

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid method"}, status=405)


# -----------------------------
# GET TICKET BY TRACKING ID
# -----------------------------
@csrf_exempt
def ticket_detail(request, tracking_id):
    try:
        ticket = Ticket.objects.get(tracking_id=tracking_id)

        data = {
            "tracking_id": ticket.tracking_id,
            "title": ticket.title,
            "description": ticket.description,
            "status": ticket.status,
            "client": f"{ticket.client.first_name} {ticket.client.last_name}",
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


# -----------------------------
# Manual PDF View (Download/Preview)
# -----------------------------
def generate_auftrag(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)

    # Use SAME PDF style from utils.py
    pdf_buffer = generate_pdf(ticket)

    response = HttpResponse(pdf_buffer, content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="auftrag_{ticket.tracking_id}.pdf"'
    return response
