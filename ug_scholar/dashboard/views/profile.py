from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views import View

from ug_scholar.library.decorators import AdministratorsOnly
from ug_scholar.library.utils_functions import log_user_action


@method_decorator(AdministratorsOnly, name="dispatch")
class ProfileView(View):
    """View and update the authenticated administrator profile."""

    def get(self, request):
        return render(request, "pages/profile.html")

    def post(self, request):
        user = request.user
        fullname = (request.POST.get("fullname") or "").strip()
        email = (request.POST.get("email") or "").strip().lower()
        phone = (request.POST.get("phone") or "").strip()
        password = request.POST.get("password") or ""
        password2 = request.POST.get("password2") or ""

        if password != password2:
            log_user_action(
                user,
                "Attempted to change password but passwords did not match",
            )
            messages.error(request, "Passwords do not match")
            return redirect("dashboard:profile")

        changed_fields = []
        for field, value in (
            ("email", email),
            ("fullname", fullname),
            ("phone", phone),
        ):
            if getattr(user, field) != value:
                setattr(user, field, value)
                changed_fields.append(field)

        if password:
            user.set_password(password)
            changed_fields.append("password")
        if changed_fields:
            user.save(update_fields=changed_fields)
        if password:
            # A password change updates the auth hash. Refreshing this session
            # prevents the administrator who made the change from being logged out.
            update_session_auth_hash(request, user)

        log_user_action(user, "Updated their profile")
        messages.info(request, "Profile Updated Successfully")
        return redirect("dashboard:profile")


@method_decorator(AdministratorsOnly, name="dispatch")
class ChangeProfilePictureView(View):
    """Change the current administrator's profile picture."""

    def get(self, request):
        return redirect("dashboard:profile")

    def post(self, request):
        user = request.user
        profile_picture = request.FILES.get("profile_picture")
        if profile_picture:
            user.profile_picture = profile_picture
            user.save(update_fields=["profile_picture"])
            log_user_action(user, "Updated their profile picture")
            messages.info(request, "Profile Picture Updated Successfully")
        else:
            log_user_action(
                user,
                "Attempted to update their profile picture but no picture was uploaded",
            )
            messages.error(request, "Profile Picture Not Updated")
        return redirect("dashboard:profile")
