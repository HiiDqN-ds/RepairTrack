from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.urls import reverse
from tickets.models import Ticket
from django.contrib import messages

# -----------------------------
# Staff Authentication
# -----------------------------
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.utils.http import url_has_allowed_host_and_scheme
from django.conf import settings

def staff_login(request):
    """Staff login page"""
    next_url = request.GET.get("next") or request.POST.get("next") or '/staff/dashboard/'

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user and user.is_staff:
            login(request, user)
            
            # Safety check to prevent open redirect
            if url_has_allowed_host_and_scheme(next_url, allowed_hosts=settings.ALLOWED_HOSTS):
                return redirect(next_url)
            return redirect('/staff/dashboard/')

        return render(request, "staff/login.html", {"error": "Invalid credentials", "next": next_url})

    return render(request, "staff/login.html", {"next": next_url})



@login_required(login_url='staff:login')
def staff_logout(request):
    """Log out staff user"""
    logout(request)
    return redirect('staff:login')


# -----------------------------
# Dashboard & Ticket Views
# -----------------------------
@login_required(login_url='staff:login')
def staff_dashboard(request):
    """List all tickets in dashboard"""
    tickets = Ticket.objects.all().order_by('-created_at')
    return render(request, 'staff/dashboard.html', {'tickets': tickets})


@login_required(login_url='staff:login')
def staff_ticket_detail(request, id):
    """Detail view for a single ticket"""
    ticket = get_object_or_404(Ticket, id=id)
    return render(request, 'staff/ticket_detail.html', {'ticket': ticket})


# -----------------------------
# Update Ticket Status + Price + Notify Client
# -----------------------------
@login_required(login_url='staff:login')
def update_ticket_status(request, id):
    ticket = get_object_or_404(Ticket, id=id)

    if request.method == "POST":
        ticket.status = request.POST.get("status", ticket.status)
        price = request.POST.get("price")
        if price:
            ticket.estimated_price = price
        staff_note = request.POST.get("staff_note")
        ticket.save()

        # Send email
        subject = f"Update zu Ihrem Reparaturauftrag #{ticket.tracking_id}"
        message = f"""
Hallo {ticket.client.first_name},

Es gibt ein neues Update zu Ihrem Auftrag.

Status: {ticket.get_status_display()}
Preis: {ticket.estimated_price} €

Nachricht vom Techniker:
{staff_note or 'Keine zusätzliche Notiz.'}

Tracking Nummer: {ticket.tracking_id}

Mit freundlichen Grüßen  
Tanitech Team
"""
        try:
            send_mail(subject, message, None, [ticket.client.email], fail_silently=False)
            messages.success(request, "Update + Nachricht erfolgreich an Kunden gesendet ✅")
        except Exception as e:
            messages.error(request, f"E-Mail Fehler: {e} ❌")

        # 🔹 Redirect to dashboard after success
        return redirect('staff:dashboard')

    return redirect('staff:staff_ticket_detail', id=ticket.id)

# -----------------------------
# Delete Ticket 
# -----------------------------
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from tickets.models import Ticket

@login_required(login_url='staff:login')
def delete_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)

    if request.method == "POST":
        ticket.delete()

    return redirect('staff:dashboard')


# -----------------------------
# Printable Ticket Label
# -----------------------------
@login_required(login_url='staff:login')
def print_ticket(request, id):
    """Printable ticket for sticking on device"""
    ticket = get_object_or_404(Ticket, id=id)
    return render(request, 'staff/print_ticket.html', {'ticket': ticket})



from django.shortcuts import render, redirect
from django.core.mail import EmailMessage
from tickets.models import Ticket
from django.contrib.auth.models import User
from tickets.utils import generate_pdf

@login_required(login_url='staff:login')
def create_ticket(request):
    if request.method == "POST":
        tracking_id = request.POST.get("tracking_id")

        first = request.POST.get("client_first_name")
        last = request.POST.get("client_last_name")
        email = request.POST.get("client_email")
        phone = request.POST.get("client_phone")
        device_type = request.POST.get("device_type")
        device_model = request.POST.get("device_model")
        description = request.POST.get("problem_description")
        price = request.POST.get("estimated_price") or 0

        # Validation
        if not tracking_id:
            messages.error(request, "Tracking ID is required.")
            return redirect('staff:dashboard')

        if Ticket.objects.filter(tracking_id=tracking_id).exists():
            messages.error(request, "Tracking ID already exists.")
            return redirect('staff:dashboard')

        # Get or create client
        user, _ = User.objects.get_or_create(
            username=email,
            defaults={
                "email": email,
                "first_name": first,
                "last_name": last
            }
        )

        # Create ticket with manual tracking ID
        ticket = Ticket.objects.create(
            tracking_id=tracking_id,
            title=f"{device_type} repair",
            description=description,
            client=user,
            client_phone=phone,
            device_type=device_type,
            device_model=device_model,
            estimated_price=price
        )

        # Generate PDF
        pdf = generate_pdf(ticket)

        # Send Email
        subject = f"Reparaturauftrag #{ticket.tracking_id}"
        body = f"""Hallo {first},

Ihr Reparaturauftrag wurde erstellt.

Tracking Nummer: {ticket.tracking_id}

Das PDF finden Sie im Anhang.

Mit freundlichen Grüßen  
Tanitech Team
"""

        msg = EmailMessage(subject, body, None, [email])
        msg.attach(
            f"auftrag_{ticket.tracking_id}.pdf",
            pdf.getvalue(),
            "application/pdf"
        )
        msg.send()

        messages.success(request, "Ticket created and email sent successfully.")
        return redirect("staff:dashboard")

    # If someone opens URL manually
    return redirect("staff:dashboard")
