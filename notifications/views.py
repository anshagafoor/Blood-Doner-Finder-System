from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Notification


@login_required
def notification_list(request):
    notes = request.user.notifications.all()
    return render(request, "notifications/list.html", {"notes": notes})


@login_required
def mark_read(request, pk):
    note = get_object_or_404(Notification, pk=pk, recipient=request.user)
    note.is_read = True
    note.save(update_fields=["is_read"])
    if note.link:
        return redirect(note.link)
    return redirect("notifications:list")


@login_required
def mark_all_read(request):
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return redirect("notifications:list")
