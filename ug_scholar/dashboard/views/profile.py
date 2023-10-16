from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views import View

from ug_scholar.library.decorators import AdministratorsOnly
from ug_scholar.library.utils_functions import log_user_action


class ProfileView(View):
    '''Profile view - view and update user profile - /profile/'''
    
    @method_decorator(AdministratorsOnly)
    def get(self, request):
        return render(request, "pages/profile.html")
    
    @method_decorator(AdministratorsOnly)
    def post(self, request):
        user = request.user
        fullname = request.POST.get('fullname')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        
        if password != password2:
            log_user_action(user, "Attempted to change password but passwords did not match")
            messages.error(request, "Passwords do not match")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
        
        if user.email != email:
            user.email = email
            user.save()
        
        if user.fullname != fullname:
            user.fullname = fullname
            user.save()
            
        if user.phone != phone:
            user.phone = phone
            user.save()
        
        if password:
            user.set_password(password)
            user.save()
        log_user_action(user, "Updated their profile")
        messages.info(request, "Profile Updated Successfully")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    
    
class ChangeProfilePictureView(View):
    '''Used to change the profile picture of current user'''
    
    @method_decorator(AdministratorsOnly)
    def get(self, request):
        return redirect('dashboard:profile')
    
    def post(self, request):
        user = request.user
        profile_picture = request.FILES.get('profile_picture')
        if profile_picture:
            user.profile_picture = profile_picture
            user.save()
            log_user_action(user, "Updated their profile picture")
            messages.info(request, "Profile Picture Updated Successfully")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            log_user_action(user, "Attempted to update their profile picture but no picture was uploaded")
            messages.error(request, "Profile Picture Not Updated")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))