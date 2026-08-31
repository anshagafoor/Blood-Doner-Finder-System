def unread_notifications(request):
    """Expose unread notification count + latest few to all templates."""
    if not request.user.is_authenticated:
        return {"unread_count": 0, "recent_notifications": []}
    qs = request.user.notifications.all()
    return {
        "unread_count": qs.filter(is_read=False).count(),
        "recent_notifications": qs[:6],
    }
