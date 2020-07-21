from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator
import uuid


class UserManager(BaseUserManager):
    def create_user(self, full_name, email, password=None):
        if not full_name:
            raise ValueError("Please enter your fullname")
        if not email:
            raise ValueError("Please enter an email address")
        if not password:
            raise ValueError("Please provide a password")
        user = self.model(full_name=full_name, email=self.normalize_email(email))
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, full_name, email, password=None):
        """
        Create and return a `User` with superuser powers.
        Superuser powers means that this use is an admin that can do anything
        they want.
        """
        if password is None:
            raise TypeError('Superusers must have a password.')

        user = self.create_user(full_name=full_name, email=email, password=password)
        user.jyolsyan = True
        user.mentor = True
        user.admin = True
        user.save(using=self._db)
        return user


def id_gen():
    uid = uuid.uuid4()
    return uid.hex


class User(AbstractBaseUser, PermissionsMixin):
    id = models.CharField(max_length=32, primary_key=True, default=id_gen, editable=False)
    email = models.EmailField(max_length=255, unique=True)
    full_name = models.CharField(max_length=255, blank=False)
    customer = models.BooleanField('customer', default=False)
    jyolsyan = models.BooleanField('jyolsyan ', default=False)
    mentor = models.BooleanField('mentor', default=False)
    admin = models.BooleanField('admin', default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    objects = UserManager()
    is_active = models.BooleanField(default=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.full_name

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_customer(self):
        return self.customer

    @property
    def is_jyolsyan(self):
        return self.jyolsyan

    @property
    def is_mentor(self):
        return self.mentor

    @property
    def is_staff(self):
        return self.admin

    @property
    def is_superuser(self):
        return self.admin


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    dob = models.CharField(max_length=11, null=True, blank=True)
    birthtime = models.CharField(max_length=255, null=True, blank=True)
    dst = models.CharField(max_length=255, null=True, blank=True)
    birthplace = models.CharField(max_length=255, null=True, blank=True)
    latlong = models.CharField(max_length=255, null=True, blank=True)
    mobile = models.CharField(max_length=15, blank=True)
    address = models.CharField(max_length=255, blank=True)
    state = models.CharField(max_length=255, blank=True)
    pincode = models.CharField(max_length=6, validators=[RegexValidator(r'^\d{1,10}$')], null=True)
    qualification = models.CharField(max_length=255, blank=True)
    stream = models.CharField(max_length=255, blank=True)
    institute = models.CharField(max_length=255, blank=True)
    mark = models.CharField(max_length=6, blank=True)
    gender = models.CharField(max_length=255, null=True, blank=True)
    siblings = models.CharField(max_length=255, null=True, blank=True)
    contact = models.CharField(max_length=255, null=True, blank=True)
    hobbies = models.CharField(max_length=255, null=True, blank=True)
    guardian_name = models.CharField(max_length=255, null=True, blank=True)
    career_concern = models.CharField(max_length=255, null=True, blank=True)
    personal_concern = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return 'Profile of user: {}'.format(self.user.full_name)
