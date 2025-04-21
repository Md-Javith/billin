from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
import uuid


# Create your models here.
class Company(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    is_active = models.BooleanField(default=True)
    # company_logo = models.ImageField(upload_to=user_company_logo_path, null=True, blank=True)
    registered_by = models.ForeignKey("User", on_delete=models.CASCADE, related_name='registered_companies')
    industries_type = models.CharField(max_length=255, null=True, blank=True)
    country_region = models.CharField(max_length=255, null=True, blank=True)
    timezone = models.CharField(max_length=255, null=True, blank=True)
    date_format = models.CharField(max_length=255, null=True, blank=True)
    time_format = models.CharField(max_length=255, null=True, blank=True)
    contact_person = models.CharField(max_length=255,null=True,blank=True)
    website = models.CharField(max_length=255, null=True, blank=True)
    
    
class Branch(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    is_active = models.BooleanField(default=True)
    registered_by = models.ForeignKey("User", on_delete=models.CASCADE, related_name='registered_branches')
    company  = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='company', null = True)
    contact_person = models.CharField(max_length=255,null=True,blank=True)
    phone_number = models.CharField(max_length=10, unique=True, blank=True, null=True)

   

class User(AbstractUser):
    username = models.CharField(unique=True, max_length=50,null=True, blank=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True, max_length=254)
    password = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=10,unique=True, blank=True, null=True, validators=[RegexValidator(regex=r"^\d{10}", message="Phone number must be 10 digits only.")])
    company_admin = models.BooleanField(default=False)
    company = models.ForeignKey("Company",on_delete=models.CASCADE, related_name="assign_company", null=True)
    branch_admin = models.BooleanField(default=False)
    branch = models.ForeignKey("Branch", null=True, blank=True, related_name="Branch", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    otp = models.CharField(max_length=6, null=True, blank=True)
    otp_expiry = models.DateTimeField(blank=True, null=True)
    max_otp_try = models.CharField(max_length=2, default=3)
    otp_max_out = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)