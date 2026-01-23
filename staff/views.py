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
def staff_login(request):
    """Staff login page"""
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user and user.is_staff:
            login(request, user)
            return redirect('staff:dashboard')

        return render(request, "staff/login.html", {"error": "Invalid credentials"})

    return render(request, "staff/login.html")


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
    """Update ticket status + price and notify client by email"""
    ticket = get_object_or_404(Ticket, id=id)

    if request.method == "POST":
        # Get values from form
        new_status = request.POST.get("status", ticket.status)
        new_price = request.POST.get("price")

        # Update status
        ticket.status = new_status

        # Update price ONLY if provided
        if new_price:
            try:
                ticket.estimated_price = float(new_price)
            except ValueError:
                messages.error(request, "Invalid price format ❌")
                return redirect('staff:staff_ticket_detail', id=ticket.id)

        # Save changes to database
        ticket.save()

        # Send email notification
        subject = f"Update: Your Repair Status is now '{ticket.status}'"
        message = (
            f"Hello {ticket.client.first_name},\n\n"
            f"Your ticket with tracking number {ticket.tracking_id} has been updated.\n"
            f"New status: {ticket.status}\n"
        )

        if ticket.estimated_price:
            message += f"Estimated price: {ticket.estimated_price} €\n"

        message += "\nThanks,\nTanitech Team"

        try:
            send_mail(
                subject,
                message,
                None,
                [ticket.client.email],
                fail_silently=False
            )
            messages.success(request, f"Saved and email sent to {ticket.client.email} ✅")
        except Exception as e:
            messages.error(request, f"Saved, but email failed: {e} ❌")

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
