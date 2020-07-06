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

def channel_gen():
    uid = uuid.uuid4()
    return uid.hex  

def invoice_gen():
        uid = uuid.uuid4()
        last_invoice = UserPurchases.objects.all().order_by('id').last()
        if not last_invoice:
            return 'BHVI-'+uid.hex
        new_invoice_no = 'BHVI-' + str(uid.hex)
        return new_invoice_no         

def product_gen():
        uid = uuid.uuid4()
        last_prod = Product.objects.all().order_by('id').last()
        if not last_prod:
            return 'PROD-'+uid.hex
        prod_id = 'PROD-' + str(uid.hex)
        return prod_id

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
    is_active      = models.BooleanField(default=False)
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
    dob = models.CharField(max_length=11,null=True, blank=True)
    birthtime = models.CharField(max_length=255,null=True, blank=True)
    dst = models.CharField(max_length=255,null=True, blank=True)
    birthplace = models.CharField(max_length=255,null=True, blank=True)
    latlong = models.CharField(max_length=255,null=True, blank=True)
    mobile = models.CharField(max_length=15, blank=True)
    address = models.CharField(max_length=255, blank=True)
    state = models.CharField(max_length=255, blank=True)
    pincode = models.CharField(max_length=6, validators=[RegexValidator(r'^\d{1,10}$')], null=True)
    qualification = models.CharField(max_length=255, blank=True)
    stream = models.CharField(max_length=255, blank=True)
    institute = models.CharField(max_length=255, blank=True)
    mark = models.CharField(max_length=6, blank=True)
    gender = models.CharField(max_length=255,null=True, blank=True)
    siblings = models.CharField(max_length=255,null=True, blank=True)
    contact = models.CharField(max_length=255,null=True, blank=True)    
    hobbies = models.CharField(max_length=255,null=True, blank=True)
    guardian_name = models.CharField(max_length=255,null=True, blank=True)
    career_concern = models.CharField(max_length=255,null=True, blank=True)
    personal_concern = models.CharField(max_length=255,null=True, blank=True)

    def __str__(self):
        return 'Profile of user: {}'.format(self.user.full_name)
    
class Product(models.Model):
    id = models.CharField(max_length=255, default=product_gen, primary_key=True, editable=False)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    amount = models.FloatField()
    active_discount = models.FloatField()
    call_required = models.BooleanField(default=0)
    is_package = models.BooleanField(default=0) 
    prod_type = models.CharField(default="O", max_length=2) 
    # O for other, M for mentoring, J for astrology
    active = models.BooleanField(default=1)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'Product name: {}'.format(self.name) 

class ProductFeatures(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    feature = models.CharField(max_length=255)

    def __str__(self):
        return 'Product name: {}'.format(self.product.name) 

class ProductPackages(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='package_product')
    package = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_package')

    def __str__(self):
        return 'Package name: {}'.format(self.package.name)         

class MentorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='mentor_profile')
    tags = models.CharField(max_length=255)
    experience = models.IntegerField(default=0)
    active = models.BooleanField(default=1)
    verified = models.BooleanField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'Mentor: {}'.format(self.user.full_name) 
    @property
    def mentor_type(self):
        if self.user.mentor:
            return 1 
        else:
            return 2   

class MentorProducts(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    mentor = models.ForeignKey(MentorProfile, on_delete=models.CASCADE)

    def __str__(self):
        return 'Associated Product name: {}'.format(self.product.name)                                  

class UserPurchases(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    status = models.BooleanField(default=0)
    payment_progress = models.BooleanField(default=1)
    invoice = models.CharField(max_length=255, default=invoice_gen)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'Receipt id: {}'.format(self.invoice) 

class RazorPayTransactions(models.Model):
    purchase = models.ForeignKey(UserPurchases, on_delete=models.CASCADE, related_name='transaction_details')
    razorpay_order_id = models.CharField(max_length=255, blank=True)
    razorpay_payment_id = models.CharField(max_length=255, blank=True)
    razorpay_signature = models.CharField(max_length=255, blank=True)
    status = models.BooleanField(default=0)
    refund = models.BooleanField(default=0)
    refund_date = models.DateTimeField(blank=True, null=True)
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'Transaction id: {}'.format(self.id)

    @property
    def product_refunded(self):
        return self.refund
    @property
    def transaction_success(self):
        return self.status                  

class MentorCallRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mentor_request', null=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    request_date = models.CharField(max_length=20, blank=True)
    requested_slot = models.CharField(max_length=20, blank=True)
    language = models.CharField(max_length=255,null=True, blank=True)
    query1 = models.CharField(max_length=255,null=True, blank=True)
    query2 = models.CharField(max_length=255,null=True, blank=True)
    # #bride details and groom details
    # bname = models.CharField(max_length=255,null=True, blank=True)
    # bdob = models.CharField(max_length=255,null=True, blank=True)
    # btime = models.CharField(max_length=255,null=True, blank=True)
    # bplace = models.CharField(max_length=255,null=True, blank=True)
    # blatlong = models.CharField(max_length=255,null=True, blank=True)
    # gname = models.CharField(max_length=255,null=True, blank=True)
    # gdob = models.CharField(max_length=255,null=True, blank=True)
    # gtime = models.CharField(max_length=255,null=True, blank=True)
    # gplace = models.CharField(max_length=255,null=True, blank=True)
    # glatlong = models.CharField(max_length=255,null=True, blank=True)
    # # muhurtam details
    # bname = models.CharField(max_length=255,null=True, blank=True)
    # bdob = models.CharField(max_length=255,null=True, blank=True)
    # btime = models.CharField(max_length=255,null=True, blank=True)
    # bplace = models.CharField(max_length=255,null=True, blank=True)
    # blatlong = models.CharField(max_length=255,null=True, blank=True)

    responded = models.BooleanField(default=0)
    scheduled = models.BooleanField(default=0)
    closed = models.BooleanField(default=0)
    report_submitted = models.BooleanField(default=1)
    timestamp = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return 'Request id {} Mentor type: {}'.format(self.id, self.product.name) 

class RequestedSchedules(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='schedule_times', null=False)
    mentor = models.ForeignKey(MentorProfile, on_delete=models.CASCADE, null=False)
    request = models.ForeignKey(MentorCallRequest, on_delete=models.CASCADE, null=False, related_name='mentor_request_schedule') 
    slot = models.DateTimeField()    
    accepted = models.BooleanField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)
   
    def __str__(self):
        return 'Mentor Call Request {} by: {} for {}'.format(self.request.id, self.user.full_name,self.mentor.user.full_name)   

class AcceptedCallSchedule(models.Model):
    schedule = models.ForeignKey(RequestedSchedules, on_delete=models.CASCADE, null=False, related_name='accepted_schedule') 
    completed = models.BooleanField(default=0)
    channel = models.CharField(max_length=255, default=channel_gen)
    token = models.CharField(max_length=255, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'Schedule id: {}'.format(self.schedule.id)   

class Coupon(models.Model):
    code = models.CharField(max_length=255)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)                            
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
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'User name: {}'.format(self.user.full_name) 

class FinalMentorReport(models.Model): 

    call = models.ForeignKey(MentorCallRequest, on_delete=models.CASCADE, null=False, related_name='report_schedule') 
    requirement = models.TextField(null=True, blank=True)
    diagnosis = models.TextField(null=True, blank=True)
    findings = models.TextField(null=True, blank=True)
    suggestions = models.TextField(null=True, blank=True)
    recommendation = models.TextField(null=True, blank=True)
    accepted = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
