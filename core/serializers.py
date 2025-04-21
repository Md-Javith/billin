from rest_framework import serializers
from rest_framework import generics
from core.models import User, Company, Branch
from django.db import transaction
from django.contrib.auth import get_user_model


class CompanyAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.is_staff = True
        instance.save()
        return instance     
    
    
    
    
class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = "__all__"
        
User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password', 'phone_number']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.is_staff = True  # Optional: make user staff/admin
        instance.save()
        return instance
User = get_user_model()

class BranchSerializer(serializers.ModelSerializer):
    branch_admin_user = UserSerializer(write_only=True)

    class Meta:
        model = Branch
        fields = [
            'name',
            'address',
            'contact_person',
            'phone_number',
            'branch_admin_user'
        ]

    @transaction.atomic
    def create(self, validated_data):
        request_user = self.context['request'].user
        user_data = validated_data.pop('branch_admin_user')

        # Create the branch
        branch = Branch.objects.create(
            registered_by=request_user,
            company=request_user.company,
            **validated_data
        )

        # Prepare and create the branch admin user
        password = user_data.pop('password')
        user = User(
            **user_data,
            company=request_user.company,
            branch=branch,
            branch_admin=True
        )
        user.set_password(password)  # 🔐 Hash password
        user.save()

        return branch