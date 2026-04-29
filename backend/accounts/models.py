"""accounts/models.py"""
import uuid
import pyotp
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', CustomUser.Role.STAFF)
        extra_fields.setdefault('is_active', True)   # ← add this
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):

    class Role(models.TextChoices):
        STAFF    = 'staff',    'Staff'
        CUSTOMER = 'customer', 'Customer'
        SUPPLIER = 'supplier', 'Supplier'

    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email      = models.EmailField(unique=True)
    name       = models.CharField(max_length=150, blank=True)
    role       = models.CharField(max_length=10, choices=Role.choices, default=Role.CUSTOMER)
    company    = models.CharField(max_length=200, blank=True)
    phone      = models.CharField(max_length=30, blank=True)
    

    # 2FA
    totp_secret  = models.CharField(max_length=64, blank=True, default='')
    totp_enabled = models.BooleanField(default=False)

    # Invitation-only — staff must activate new accounts
    is_active  = models.BooleanField(default=False)
    is_staff   = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        ordering = ['email']

    def __str__(self):
        return self.email

    def get_totp_uri(self):
        """Return the otpauth:// URI for QR code generation."""
        return pyotp.totp.TOTP(self.totp_secret).provisioning_uri(
            name=self.email,
            issuer_name='Ewan Millar Ltd'
        )

    def verify_totp(self, code):
        """Verify a TOTP code. Allows 30s clock drift."""
        if not self.totp_secret:
            return False
        totp = pyotp.TOTP(self.totp_secret)
        return totp.verify(code, valid_window=1)
