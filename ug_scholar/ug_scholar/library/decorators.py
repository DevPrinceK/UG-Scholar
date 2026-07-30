from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect


def AdministratorsOnly(view_function):
    """Allow access only to authenticated staff and superusers."""

    @wraps(view_function)
    def wrapped(request, *args, **kwargs):
        if request.user.is_authenticated and (
            request.user.is_superuser or request.user.is_staff
        ):
            return view_function(request, *args, **kwargs)
        messages.info(request, "Access Denied!")
        return redirect("dashboard:index")

    return wrapped
