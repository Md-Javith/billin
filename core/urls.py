from django.contrib import admin
from django.urls import path, include
from .views import CompanyAdminView, LoginView, CompanyRegistrationView, BranchWithUserCreateView


urlpatterns = [
    path('login', LoginView.as_view(), name='login'),
    path("company-admin",CompanyAdminView.as_view(), name="company admin_register"),
    path("company-registration", CompanyRegistrationView.as_view(), name="company_registration"),
    path('branch-user', BranchWithUserCreateView.as_view(), name="branch_user"),
   
    

]