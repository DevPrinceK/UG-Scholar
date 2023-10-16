from django.contrib import messages
from django.shortcuts import redirect


class AdministratorsOnly(object):
    '''Decorator to allow access to only staff and superusers'''

    def __init__(self, original_method):
        self.original_method = original_method

    def __call__(self, request, *args,  **kwargs):
        if request.user.is_authenticated:
            if (request.user.is_superuser or request.user.is_staff):  # noqa
                return self.original_method(request, *args, **kwargs)
            else:
                messages.info(request, "Access Denied!")  # noqa
                return redirect('dashboard:index')
        else:
            messages.info(request, 'Access Denied!')  # noqa
            return redirect('dashboard:index')
