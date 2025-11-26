from django.db import models

# Create your models here.
# backend/api/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django_otp.plugins.otp_email.models import EmailDevice

class CustomUserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    
    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('role', 'EMPLOYEE')  # Default role
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'ADMIN')  # Superusers are admins

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('EMPLOYEE', 'Employee'),
        ('ADMIN', 'Admin'),
    ]
    
    username = None
    email = models.EmailField(_('email address'), unique=True)
    is_2fa_enabled = models.BooleanField(default=False)
    otp_secret = models.CharField(max_length=16, blank=True)
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='EMPLOYEE',
        help_text='User role in the system'
    )
    department = models.CharField(max_length=100, blank=True, help_text='Employee department')
    employee_id = models.CharField(max_length=20, blank=True, help_text='Employee ID number')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"
    
    def enable_2fa(self):
        """Enable 2FA for this user"""
        self.is_2fa_enabled = True
        self.save()
        
    def disable_2fa(self):
        """Disable 2FA for this user"""
        self.is_2fa_enabled = False
        self.save()
        
    def create_email_device(self):
        """Create or get email device for 2FA"""
        device, created = EmailDevice.objects.get_or_create(
            user=self,
            defaults={'name': 'Email Device', 'confirmed': True}
        )
        return device
    
    def is_admin(self):
        """Check if user is admin"""
        return self.role == 'ADMIN'
    
    def is_employee(self):
        """Check if user is employee"""
        return self.role == 'EMPLOYEE'