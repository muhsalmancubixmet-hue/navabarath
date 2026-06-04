from .models import ActivityLog


def log_activity(user, action_message):
    if user and user.is_authenticated:
        ActivityLog.objects.create(user=user, action=action_message)
    elif not user:
        ActivityLog.objects.create(user=None, action=action_message)