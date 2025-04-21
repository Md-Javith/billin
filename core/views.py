from django.shortcuts import render

# Create your views here.

from datetime import timedelta
import traceback
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status  # Add this import
from django.dispatch import receiver
from django.db.models.signals import post_save
from drf_spectacular.utils import extend_schema
from rest_framework import status
from core.models import User, Company, Branch
from core.serializers import *
from rest_framework.permissions import AllowAny, IsAuthenticated
import traceback
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema
from django.http import JsonResponse
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied




class CompanyAdminView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request={
            'application/json': {
                'properties': {
                    'email': {'type': 'string'},
                    'first_name': {'type': 'string'},
                    'last_name': {'type': 'string'},
                    'username': {'type': 'string'},
                    'phone_number': {'type': 'string'},  # Should be string, not number
                    'password': {'type': 'string'},
                }
            }
        }
    )
    def post(self, request):
        try:
            serializer = CompanyAdminSerializer(data=request.data)
            if serializer.is_valid():
                # Save user as company admin
                user = serializer.save(company_admin=True)

                try:
                    send_welcome_email_company_owner(sender=self.__class__, instance=user, created=True)
                except Exception as e:
                    traceback.print_exc()
                    return Response({"Message": "Failed to send welcome email.", "Exception": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                refresh = RefreshToken.for_user(user)
                access_token = refresh.access_token

                return Response({
                    'token': {'refresh': str(refresh), 'access': str(access_token)},
                    'admin': user.company_admin
                }, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            traceback.print_exc()
            return Response({"Message": "Internal Server Error", "Exception": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@receiver(post_save, sender=User)
def send_welcome_email_company_owner(sender, instance, created, **kwargs):
    if created:  # Ensure email is only sent when the user is first created
        subject = 'Welcome to Wesscosoft Technologies Pvt Ltd.'
        message = f'''
            <html>
            <body>
                <p>Thank you for registering with novafusion Technologies Pvt Ltd.</p>
                <p>Welcome to our community!</p>
            </body>
            </html>
        '''
        from_email = 'support@wesscosoft.com'
        to_email = [instance.email]
        send_mail(subject, message, from_email, to_email, fail_silently=False, html_message=message)


class CompanyRegistrationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Check if the user has already registered a company
        if Company.objects.filter(registered_by=request.user).exists():
            return Response({"Message": "User already has a company associated with them"}, status=status.HTTP_400_BAD_REQUEST)

        # Make a mutable copy of request data
        serializer_data = request.data.copy()
        serializer_data['registered_by'] = request.user.id  # Set 'registered_by' to authenticated user ID
        serializer = CompanySerializer(data=serializer_data)
        serializer.is_valid(raise_exception=True)
        company = serializer.save()
        
        # Assign the company ID to the user
        # Reload the user from the database and assign company
        user = User.objects.get(id=request.user.id)
        user.company = company
        user.save()

        return Response({"message": "Company registered successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)

class BranchCreationView(APIView):
    permission_classes = [IsAuthenticated]
    
    
    def post(self, request):
        # Check if the user has already registered a company
        if Branch.objects.filter(registered_by=request.user).exists():
            return Response({"Message": "User already has a branch associated with them"}, status=status.HTTP_400_BAD_REQUEST)

        # Make a mutable copy of request data
        serializer_data = request.data.copy()
        serializer_data['registered_by'] = request.user.id  # Set 'registered_by' to authenticated user ID
        serializer = BranchSerializer(data=serializer_data)
        serializer.is_valid(raise_exception=True)
        company = serializer.save()
        return Response({"message": "Company registered successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
    
    

class BranchWithUserCreateView(generics.CreateAPIView):
    serializer_class = BranchSerializer
    permission_classes = [permissions.IsAuthenticated]

    def check_permissions(self, request):
        super().check_permissions(request)
        if not request.user.company_admin:
            raise PermissionDenied("Only company admins can create branches.")

   
class LoginView(APIView):
    permission_classes = [AllowAny]
    
    @extend_schema(
    request ={
        'application/json':{
            'properties':{
                'email': {'type':'string'},
                'password':{'type':'string'}
                
            }
        }
    })
    
    def post(self, request):
        try:
            email = request.data.get('email')
            password = request.data.get('password')
            
            user = User.objects.filter(email=email).first()
            
            if user is None:
                return Response('User not found')
            
            if not user.check_password(password):
                return Response('Invalid Password')
            
            refresh = RefreshToken.for_user(user)
            token = {
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            }
            user_info={
                'id':user.id,
                'username':user.username,
                'email':user.email
                
            }
            admin = user.company_admin
            
            response = JsonResponse({'value':user_info, 'token':token, 'admin':admin})
            response.set_cookie(key='x-login-token', value=token['access'], httponly=True, secure=True)
            return response
        except AuthenticationFailed as e:
            return JsonResponse({"message": str(e)}, status=401)
        except Exception as e:
            return JsonResponse({"message": "Internal Server Error", "exception": str(e)}, status=500)
        
        

    