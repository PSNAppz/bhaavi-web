
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.forms.utils import ValidationError
from .models import User
from .models import RequestedSchedules
from django import forms


class RegisterUserForm(UserCreationForm):

	class Meta(UserCreationForm.Meta):
		model = User
		fields = ['full_name', 'email', 'password1', 'password2']

	def save(self, commit=True):
		user = super().save(commit=False)
		user.customer = True
		if commit:
			user.save()
		return user

	def check_name(self):
		full_name = self.cleaned_data.get('name')
		return full_name	

	def clean_email(self):
		email = self.cleaned_data.get('email')
		qs = User.objects.filter(email=email)
		if qs.exists():
			raise forms.ValidationError("Email already registered")
		return email

	def clean_password2(self):
        # Check that the two password entries match
		password1 = self.cleaned_data.get("password1")
		password2 = self.cleaned_data.get("password2")
		if password1 and password2 and password1 != password2:
			raise forms.ValidationError("Passwords don't match")
		return password2

class RegisterMentorForm(UserCreationForm):

	class Meta(UserCreationForm.Meta):
		model = User
		fields = ['full_name', 'email', 'password1', 'password2']

	def save(self, commit=True):
		user = super().save(commit=False)
		user.mentor = True
		if commit:
			user.save()
		return user

	def check_name(self):
		full_name = self.cleaned_data.get('name')
		return full_name	

	def clean_email(self):
		email = self.cleaned_data.get('email')
		qs = User.objects.filter(email=email)
		if qs.exists():
			raise forms.ValidationError("Email already registered")
		return email

	def clean_password2(self):
        # Check that the two password entries match
		password1 = self.cleaned_data.get("password1")
		password2 = self.cleaned_data.get("password2")
		if password1 and password2 and password1 != password2:
			raise forms.ValidationError("Passwords don't match")
		return password2


class RegisterJyolsyanForm(UserCreationForm):

	class Meta(UserCreationForm.Meta):
		model = User
		fields = ['full_name', 'email', 'password1', 'password2']

	def save(self, commit=True):
		user = super().save(commit=False)
		user.jyolsyan = True
		if commit:
			user.save()
		return user

	def check_name(self):
		full_name = self.cleaned_data.get('name')
		return full_name	

	def clean_email(self):
		email = self.cleaned_data.get('email')
		qs = User.objects.filter(email=email)
		if qs.exists():
			raise forms.ValidationError("Email already registered")
		return email

	def clean_password2(self):
        # Check that the two password entries match
		password1 = self.cleaned_data.get("password1")
		password2 = self.cleaned_data.get("password2")
		if password1 and password2 and password1 != password2:
			raise forms.ValidationError("Passwords don't match")
		return password2

class UserAdminCreationForm(forms.ModelForm):
	
	password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
	password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)
	
	class Meta:
		model = User
		fields = ('email', 'password1', 'full_name')

	def clean_password2(self):
        # Check that the two password entries match
		password1 = self.cleaned_data.get("password1")
		password2 = self.cleaned_data.get("password2")
		if password1 and password2 and password1 != password2:
			raise forms.ValidationError("Passwords don't match")
		return password2

	def save(self, commit=True):
        # Save the provided password in hashed format
		user = super(UserAdminCreationForm, self).save(commit=False)
		user.set_password(self.cleaned_data["password1"])
		if commit:
			user.save()
		return user


class UserAdminChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('email', 'password', 'full_name')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class LoginForm(forms.Form):

	def __init__(self, request, *args, **kwargs):
		self.request = request
		super(LoginForm, self).__init__(*args, **kwargs)

	def clean(self):
		request = self.request
		data = self.cleaned_data
		email  = data.get("email")
		password  = data.get("password")
		full_name = data.get("name")
		# qs = User.objects.filter(email=email)
		# if qs.exists():
		#     # user email is registered, check active/
		#     not_active = qs.filter(is_active=False)
		#     if not_active.exists():
		#         ## not active, check email activation
		#         link = reverse("account:resend-activation")
		#         reconfirm_msg = """Go to <a href='{resend_link}'>
		#         resend confirmation email</a>.
		#         """.format(resend_link = link)
		#         confirm_email = EmailActivation.objects.filter(email=email)
		#         is_confirmable = confirm_email.confirmable().exists()
		#         if is_confirmable:
		#             msg1 = "Please check your email to confirm your account or " + reconfirm_msg.lower()
		#             raise forms.ValidationError(mark_safe(msg1))
		#         email_confirm_exists = EmailActivation.objects.email_exists(email).exists()
		#         if email_confirm_exists:
		#             msg2 = "Email not confirmed. " + reconfirm_msg
		#             raise forms.ValidationError(mark_safe(msg2))
		#         if not is_confirmable and not email_confirm_exists:
		#             raise forms.ValidationError("This user is inactive.")
		user = authenticate(request, email=email, password=password)
		if user is None:
			raise forms.ValidationError("Invalid credentials")
		login(request, user)
		self.user = user
		return data


class ScheduleRequestForm(forms.ModelForm):

	class Meta:
		model = RequestedSchedules
		fields = ('user',)

    