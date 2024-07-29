import random
import string
import uuid

from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin, User)
from django.db import models


class Avatar(models.Model):
    photo_url = models.ImageField(upload_to='users_avatar', null=True, blank=True)


class UserAccountManager(BaseUserManager):
    def create_user(self, email, password=None, refferalcode=None, nikname=None):
        if not email:
            raise ValueError('Введите адрес электронной почты')
        email = self.normalize_email(email)
        user = self.model(email=email, refferalcode=refferalcode)

        if nikname:
            user.nikname = nikname
        else:
            user.nikname = 'user' + uuid.uuid4().hex[:10]

        user.securecode = uuid.uuid4().hex[:16]
        user.generate_activation_code()
        user.set_password(password)
        user.save()

        return user


class User(AbstractBaseUser):
    email = models.EmailField(max_length=256, unique=True)
    nikname = models.CharField(max_length=256, unique=True, blank=True)
    avatar_id = models.ForeignKey(Avatar, on_delete=models.SET_NULL, null=True, blank=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    FA = models.BooleanField(default=False)
    refferalcode = models.CharField(max_length=20, null=True, blank=True)
    securecode = models.CharField(max_length=20)
    is_active = models.BooleanField(default=False)
    activation_code = models.CharField(max_length=4, null=True, blank=True)

    objects = UserAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['refferalcode', 'nikname']

    def generate_activation_code(self):
        self.activation_code = ''.join(random.choices(string.digits, k=4))
        self.save()

    def save(self, *args, **kwargs):
        if not self.activation_code:
            self.generate_activation_code()
        super(User, self).save(*args, **kwargs)


class Refferal(models.Model):
    refferar = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referrals_made')
    refferal = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referrals_received')


class UserStatus(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time_bunned_end = models.DateTimeField(null=True, blank=True)
    time_muted_end = models.DateTimeField(null=True, blank=True)


