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
    id             = models.CharField(max_length=32, primary_key=True, default=id_gen, editable=False)
    email          = models.EmailField(max_length=255, unique=True)
    full_name      = models.CharField(max_length=255, blank=False)
    customer       = models.BooleanField('customer', default=False)
    jyolsyan       = models.BooleanField('jyolsyan ',default=False)
    mentor         = models.BooleanField('mentor', default=False)
    admin          = models.BooleanField('admin', default=False)
    timestamp      = models.DateTimeField(auto_now_add=True)
    objects        = UserManager()
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
    dob = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=255, blank=True)
    state = models.CharField(max_length=255, blank=True)
    pincode = models.CharField(max_length=6, validators=[RegexValidator(r'^\d{1,10}$')], null=True)
    father = models.CharField(max_length=255, blank=True)
    mother = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return 'Profile of user: {}'.format(self.user.full_name)

class MentorProfile(models.Model):
    MENTOR_TYPES=(
        ('J', 'Jyolsyan'),
        ('C', 'Councellor'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='mentor_profile')
    tags = models.CharField(max_length=255)
    experience = models.IntegerField
    mentor_type =  models.CharField(max_length=1, choices=MENTOR_TYPES)
    active = models.BooleanField(default=1)
    verified = models.BooleanField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'Profile of user: {}'.format(self.user.full_name)          

class AcademicProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='academic')
    dob = models.DateField()
    qualification = models.CharField(max_length=255)
    stream = models.CharField(max_length=255)
    institute = models.CharField(max_length=255)
    mark = models.CharField(max_length=6, validators=[RegexValidator(r'^\d{1,10}$')])

    def __str__(self):
        return 'Profile of user: {}'.format(self.user.full_name)
        
class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    amount = models.IntegerField()
    active = models.BooleanField(default=1)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'Product name: {}'.format(self.name)              

class CustomerPlan(models.Model):
    users = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    status = models.BooleanField(default=1)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'Plan name: {}'.format(self.product.name)   

class CallSchedule(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='call', null=False)
    mentor = models.ForeignKey(MentorProfile, on_delete=models.CASCADE, null=False)
    slot = models.DateTimeField()    
    completed = models.BooleanField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'Profile of user: {}'.format(self.user.full_name)          

class RequestedSchedules(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='schedule_request', null=False)
    mentor = models.ForeignKey(MentorProfile, on_delete=models.CASCADE, null=False)
    slot = models.DateTimeField()    
    accepted = models.BooleanField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'Profile of user: {}'.format(self.user.full_name)       

class Coupon(models.Model):
    code = models.CharField(max_length=255)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='coupon', null=True)                            
    discount_percent = models.DecimalField( max_digits=5, decimal_places=2)
    count = models.IntegerField(default=1)
    multiple_usage = models.BooleanField(default=0)
    active = models.BooleanField(default=1)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'Product name: {}'.format(self.name) 
    @property
    def is_siteWide(self):
        if(product == ""):
             return True
        else:
            return False
    


class UserRedeemCoupon(models.Model):
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='coupon_details', null=False)   
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_details', null=False)   
    discount_percent = models.DecimalField( max_digits=5, decimal_places=2)
    usage = models.IntegerField(default=1)
    active = models.BooleanField(default=1)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'User name: {}'.format(self.user.full_name) 
