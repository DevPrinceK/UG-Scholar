from django.contrib.auth.models import BaseUserManager


class AccountManager(BaseUserManager):
    '''manages User account creation'''

    def create_user(self, email, password, fullname='-', **kwargs):
        email = self.normalize_email(email).strip().lower()
        user = self.model(email=email, fullname=fullname, **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, fullname='-', **kwargs):
        user = self.create_user(email,  password, fullname, **kwargs)  # noqa
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user
