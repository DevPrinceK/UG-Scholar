from django.contrib.auth.models import BaseUserManager


class AccountManager(BaseUserManager):
    '''manages User account creation'''

    def create_user(self, email, password, fullname='-', **kwargs):
        user = self.model(email=email, password=password, fullname=fullname, **kwargs)  # noqa
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, fullname='-', **kwargs):
        user = self.create_user(email,  password, fullname, **kwargs)  # noqa
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user
