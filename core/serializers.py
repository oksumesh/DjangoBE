from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User, UserProfile, Poll, Vote, LoyaltyTier, PollVisibility
from datetime import datetime
import json

# ==================== USER SERIALIZERS ====================

class UserSerializer(serializers.ModelSerializer):
    """Main User serializer matching Spring Boot User entity"""
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'phone_number',
            'is_active', 'email_verified', 'created_at', 'updated_at',
            'last_login_at', 'loyalty_points', 'loyalty_tier'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_login_at', 'loyalty_tier']

class CreateUserRequestSerializer(serializers.Serializer):
    """Serializer for creating new users"""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, validators=[validate_password])
    firstName = serializers.CharField(max_length=150, required=False, allow_blank=True)
    lastName = serializers.CharField(max_length=150, required=False, allow_blank=True)
    phoneNumber = serializers.CharField(max_length=20, required=False, allow_blank=True)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email already exists.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['email'],  # Use email as username
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('firstName', ''),
            last_name=validated_data.get('lastName', ''),
            phone_number=validated_data.get('phoneNumber', '')
        )
        return user

class UpdateUserRequestSerializer(serializers.Serializer):
    """Serializer for updating user information"""
    firstName = serializers.CharField(max_length=150, required=False, allow_blank=True)
    lastName = serializers.CharField(max_length=150, required=False, allow_blank=True)
    phoneNumber = serializers.CharField(max_length=20, required=False, allow_blank=True)

class AddLoyaltyPointsRequestSerializer(serializers.Serializer):
    """Serializer for adding loyalty points"""
    points = serializers.IntegerField(min_value=1)

# ==================== AUTHENTICATION SERIALIZERS ====================

class LoginRequestSerializer(serializers.Serializer):
    """Serializer for login requests"""
    email = serializers.EmailField()
    password = serializers.CharField()
    rememberMe = serializers.BooleanField(default=False)

class RegisterRequestSerializer(serializers.Serializer):
    """Serializer for registration requests"""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    firstName = serializers.CharField(max_length=150, required=False, allow_blank=True)
    lastName = serializers.CharField(max_length=150, required=False, allow_blank=True)
    phoneNumber = serializers.CharField(max_length=20, required=False, allow_blank=True)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email already exists.")
        return value

class RefreshTokenRequestSerializer(serializers.Serializer):
    """Serializer for refresh token requests"""
    refresh_token = serializers.CharField()

class ForgotPasswordRequestSerializer(serializers.Serializer):
    """Serializer for forgot password requests"""
    email = serializers.EmailField()

class VerifyOtpRequestSerializer(serializers.Serializer):
    """Serializer for OTP verification"""
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

class ResetPasswordRequestSerializer(serializers.Serializer):
    """Serializer for password reset"""
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    newPassword = serializers.CharField(write_only=True, min_length=6)

class GoogleAuthRequestSerializer(serializers.Serializer):
    """Serializer for Google OAuth authentication"""
    idToken = serializers.CharField()

class AuthResponseSerializer(serializers.Serializer):
    """Serializer for authentication responses"""
    success = serializers.BooleanField()
    message = serializers.CharField()
    token = serializers.CharField(required=False)
    user = UserSerializer(required=False)
    expiresIn = serializers.IntegerField(required=False)

# ==================== POLL SERIALIZERS ====================

class UserSummarySerializer(serializers.Serializer):
    """Serializer for user summary in poll responses"""
    id = serializers.IntegerField()
    firstName = serializers.CharField(allow_null=True)
    lastName = serializers.CharField(allow_null=True)
    email = serializers.EmailField()

class PollResponseSerializer(serializers.ModelSerializer):
    """Main Poll response serializer matching Spring Boot PollResponse"""
    createdBy = UserSummarySerializer(source='created_by', read_only=True)
    totalVotes = serializers.IntegerField(source='total_votes', read_only=True)
    error = serializers.CharField(required=False, allow_null=True)

    class Meta:
        model = Poll
        fields = [
            'id', 'question', 'options', 'votes', 'category', 'is_active',
            'is_anonymous', 'duration', 'visibility', 'image_url', 'createdBy',
            'created_at', 'updated_at', 'totalVotes', 'error'
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Format datetime fields
        if data.get('created_at'):
            data['created_at'] = instance.created_at.strftime('%Y-%m-%dT%H:%M:%S')
        if data.get('updated_at'):
            data['updated_at'] = instance.updated_at.strftime('%Y-%m-%dT%H:%M:%S')
        if data.get('duration'):
            data['duration'] = instance.duration.strftime('%Y-%m-%dT%H:%M:%S')
        return data

class CreatePollRequestSerializer(serializers.Serializer):
    """Serializer for creating polls"""
    question = serializers.CharField(max_length=500)
    options = serializers.ListField(
        child=serializers.CharField(max_length=255),
        min_length=2
    )
    category = serializers.CharField(max_length=100)
    isAnonymous = serializers.BooleanField(default=False)
    duration = serializers.DateTimeField(required=False, allow_null=True)
    visibility = serializers.ChoiceField(choices=PollVisibility.choices, default=PollVisibility.PUBLIC)
    imageUrl = serializers.URLField(required=False, allow_blank=True)
    createdByUserId = serializers.IntegerField()

    def validate_visibility(self, value):
        return value.upper()

class VoteRequestSerializer(serializers.Serializer):
    """Serializer for voting on polls"""
    option = serializers.CharField(max_length=255)
    voterUserId = serializers.IntegerField()

# ==================== RESPONSE SERIALIZERS ====================

class HealthResponseSerializer(serializers.Serializer):
    """Serializer for health check responses"""
    status = serializers.CharField()
    service = serializers.CharField()

class PollStatisticsSerializer(serializers.Serializer):
    """Serializer for poll statistics"""
    totalVotes = serializers.IntegerField()
    optionStats = serializers.DictField()
    participationRate = serializers.FloatField()

# ==================== LEGACY SERIALIZERS (for backward compatibility) ====================

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['phone', 'preferred_cinemas', 'is_verified']

class VoteSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Vote
        fields = ['id', 'user', 'poll', 'option', 'timestamp'] 