from __future__ import unicode_literals

import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from rest_framework.authtoken.models import Token
from profiles.models import Profile

class UserManager(BaseUserManager):
    def _create_user(self, email, password,
            is_staff, is_superuser, **kwargs):
        now = timezone.now()
        if not email:
            raise ValueError('An email address is required')
        email = self.normalize_email(email)
        user = self.model(email=email,
                is_staff=is_staff,
                is_superuser=is_superuser,
                last_login=now,
                date_joined=now, **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **kwargs):
        return self._create_user(email, password, False, False, **kwargs)

    def create_superuser(self, email, password, **kwargs):
        return self._create_user(email, password, True, True, **kwargs)

class User(AbstractBaseUser, PermissionsMixin):
    objects = UserManager()

    date_joined = models.DateTimeField(default=timezone.now)
    email = models.EmailField(unique=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_staff = models.BooleanField(default=False)
    #profile = models.OneToOneField(Profile)
    USERNAME_FIELD = 'email'
    pass

# Post-save signal to ensure that a token is generated when  a User is
# created.
@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
