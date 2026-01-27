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
        # Status
        new_status = request.POST.get("status", ticket.status)
        ticket.status = new_status

        # Price
        price = request.POST.get("price")
        if price:
            ticket.estimated_price = price

        # Staff note
        staff_note = request.POST.get("staff_note")

        ticket.save()

        # Build email message
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
            send_mail(
                subject,
                message,
                None,
                [ticket.client.email],
                fail_silently=False,
            )
            messages.success(request, "Update + Nachricht erfolgreich an Kunden gesendet ✅")
        except Exception as e:
            messages.error(request, f"E-Mail Fehler: {e} ❌")

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
