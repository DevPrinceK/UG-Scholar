from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View

from accounts.models import UserLog
from ug_scholar.library.decorators import AdministratorsOnly
from ug_scholar.library.utils_functions import log_user_action


class LogsView(View):
    '''Renders the logs page'''
    template_name = 'pages/logs.html'
    
    @method_decorator(AdministratorsOnly)
    def get(self, request):
        user = request.user
        logs = UserLog.objects.all().order_by("-created_at")
        context = {
           "logs": logs
        }
        log_user_action(user, "Accessed the logs page")
        return render(request, self.template_name, context)
    
    