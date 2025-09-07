from django.shortcuts import render
from rest_framework import viewsets, permissions, generics, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import Q
import random
import string
from datetime import datetime, timedelta
from google.oauth2 import id_token
from google.auth.transport import requests

from .models import User, UserProfile, Poll, Vote, LoyaltyTier, PollVisibility
from .serializers import (
    UserSerializer, CreateUserRequestSerializer, UpdateUserRequestSerializer,
    AddLoyaltyPointsRequestSerializer, LoginRequestSerializer, RegisterRequestSerializer,
    RefreshTokenRequestSerializer, ForgotPasswordRequestSerializer, VerifyOtpRequestSerializer,
    ResetPasswordRequestSerializer, GoogleAuthRequestSerializer, AuthResponseSerializer, PollResponseSerializer,
    CreatePollRequestSerializer, VoteRequestSerializer, HealthResponseSerializer,
    PollStatisticsSerializer, UserProfileSerializer, VoteSerializer
)
from .email_service import EmailService

# ==================== AUTHENTICATION VIEWS ====================

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """User registration endpoint matching Spring Boot /api/auth/register"""
    serializer = RegisterRequestSerializer(data=request.data)
    if serializer.is_valid():
        try:
            user = User.objects.create_user(
                username=serializer.validated_data['email'],
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password'],
                first_name=serializer.validated_data.get('firstName', ''),
                last_name=serializer.validated_data.get('lastName', ''),
                phone_number=serializer.validated_data.get('phoneNumber', '')
            )
            
            # Generate token
            refresh = RefreshToken.for_user(user)
            token = str(refresh.access_token)
            
            response_data = {
                'success': True,
                'message': 'Registration successful',
                'token': token,
                'user': UserSerializer(user).data,
                'expiresIn': 3600
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Registration failed: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({
        'success': False,
        'message': 'Invalid registration data',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """User login endpoint matching Spring Boot /api/auth/login"""
    serializer = LoginRequestSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        remember_me = serializer.validated_data.get('rememberMe', False)
        
        # Try to authenticate with email
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                if not user.is_active:
                    return Response({
                        'success': False,
                        'message': 'Account is deactivated'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Update last login
                user.last_login_at = timezone.now()
                user.save()
                
                # Generate token
                refresh = RefreshToken.for_user(user)
                token = str(refresh.access_token)
                
                response_data = {
                    'success': True,
                    'message': 'Login successful',
                    'token': token,
                    'user': UserSerializer(user).data,
                    'expiresIn': 86400 if remember_me else 3600
                }
                
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'message': 'Invalid email or password'
                }, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Invalid email or password'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({
        'success': False,
        'message': 'Invalid login data',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    """Token refresh endpoint matching Spring Boot /api/auth/refresh"""
    serializer = RefreshTokenRequestSerializer(data=request.data)
    if serializer.is_valid():
        # In a real implementation, you would validate the refresh token
        # For now, just return a new token
        return Response({
            'success': True,
            'message': 'Token refreshed',
            'token': 'new_token_here',
            'expiresIn': 3600
        }, status=status.HTTP_200_OK)
    
    return Response({
        'success': False,
        'message': 'Invalid refresh token'
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """Logout endpoint matching Spring Boot /api/auth/logout"""
    # In a real implementation, you would invalidate the token
    return Response({
        'message': 'Logout successful'
    }, status=status.HTTP_200_OK)

# OTP storage (in production, use Redis or database)
otp_store = {}

@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    """Forgot password endpoint matching Spring Boot /api/auth/forgot"""
    serializer = ForgotPasswordRequestSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email)
            # Generate OTP
            otp = ''.join(random.choices(string.digits, k=6))
            otp_store[email] = {
                'otp': otp,
                'expires_at': timezone.now() + timedelta(minutes=10)
            }
            
            # Send OTP via email
            user_name = f"{user.first_name} {user.last_name}".strip() if user.first_name or user.last_name else None
            email_sent = EmailService.send_otp_email(email, otp, user_name)
            
            if email_sent:
                return Response({
                    'message': f'OTP sent to {email}'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'message': 'Failed to send OTP email. Please try again.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except User.DoesNotExist:
            return Response({
                'message': 'User not found'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({
        'message': 'Invalid email'
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp(request):
    """Verify OTP endpoint matching Spring Boot /api/auth/verify-otp"""
    serializer = VerifyOtpRequestSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']
        
        entry = otp_store.get(email)
        if entry and entry['otp'] == otp and timezone.now() <= entry['expires_at']:
            return Response({
                'message': 'OTP verified successfully'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'message': 'Invalid or expired OTP'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({
        'message': 'Invalid data'
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    """Reset password endpoint matching Spring Boot /api/auth/reset-password"""
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Reset password request data: {request.data}")
    
    serializer = ResetPasswordRequestSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']
        new_password = serializer.validated_data['newPassword']
        
        entry = otp_store.get(email)
        if entry and entry['otp'] == otp and timezone.now() <= entry['expires_at']:
            try:
                user = User.objects.get(email=email)
                user.set_password(new_password)
                user.save()
                # Remove OTP from store
                del otp_store[email]
                
                # Send confirmation email
                user_name = f"{user.first_name} {user.last_name}".strip() if user.first_name or user.last_name else None
                EmailService.send_password_reset_confirmation(email, user_name)
                
                return Response({
                    'message': 'Password updated successfully'
                }, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({
                    'message': 'User not found'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                'message': 'Invalid or expired OTP'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    logger.error(f"Reset password validation errors: {serializer.errors}")
    return Response({
        'message': 'Invalid data',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def google_auth(request):
    """Google OAuth authentication endpoint"""
    serializer = GoogleAuthRequestSerializer(data=request.data)
    if serializer.is_valid():
        id_token_string = serializer.validated_data['idToken']
        
        try:
            # Verify the Google ID token using web client ID
            WEB_CLIENT_ID = '749338388642-8avu2kr7c66p6blq917dglu0v30k6tb0.apps.googleusercontent.com'
            
            idinfo = id_token.verify_oauth2_token(
                id_token_string, 
                requests.Request(), 
                WEB_CLIENT_ID
            )
            
            # Extract user information from the token
            google_id = idinfo['sub']
            email = idinfo['email']
            first_name = idinfo.get('given_name', '')
            last_name = idinfo.get('family_name', '')
            name = idinfo.get('name', '')
            
            # Check if user already exists
            try:
                user = User.objects.get(email=email)
                # Update user info if needed
                if not user.first_name and first_name:
                    user.first_name = first_name
                if not user.last_name and last_name:
                    user.last_name = last_name
                user.save()
            except User.DoesNotExist:
                # Create new user
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    # Set a random password since Google users don't have passwords
                    password=User.objects.make_random_password()
                )
            
            # Update last login
            user.last_login_at = timezone.now()
            user.save()
            
            # Generate JWT token
            refresh = RefreshToken.for_user(user)
            token = str(refresh.access_token)
            
            response_data = {
                'success': True,
                'message': 'Google authentication successful',
                'token': token,
                'user': UserSerializer(user).data,
                'expiresIn': 3600
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except ValueError as e:
            return Response({
                'success': False,
                'message': f'Invalid Google token: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Google authentication failed: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({
        'success': False,
        'message': 'Invalid request data',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

# ==================== USER MANAGEMENT VIEWS ====================

@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_users(request):
    """Get all users endpoint matching Spring Boot /api/users"""
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_user_by_id(request, id):
    """Get user by ID endpoint matching Spring Boot /api/users/{id}"""
    try:
        user = User.objects.get(id=id)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({
            'message': 'User not found'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_user_by_email(request, email):
    """Get user by email endpoint matching Spring Boot /api/users/email/{email}"""
    try:
        user = User.objects.get(email=email)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({
            'message': 'User not found'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([AllowAny])
def create_user(request):
    """Create user endpoint matching Spring Boot /api/users"""
    serializer = CreateUserRequestSerializer(data=request.data)
    if serializer.is_valid():
        try:
            user = serializer.save()
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                'message': f'Failed to create user: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({
        'message': 'Invalid user data',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([AllowAny])
def update_user(request, id):
    """Update user endpoint matching Spring Boot /api/users/{id}"""
    try:
        user = User.objects.get(id=id)
        serializer = UpdateUserRequestSerializer(data=request.data)
        if serializer.is_valid():
            if 'firstName' in serializer.validated_data:
                user.first_name = serializer.validated_data['firstName']
            if 'lastName' in serializer.validated_data:
                user.last_name = serializer.validated_data['lastName']
            if 'phoneNumber' in serializer.validated_data:
                user.phone_number = serializer.validated_data['phoneNumber']
            
            user.save()
            return Response(UserSerializer(user).data, status=status.HTTP_200_OK)
        else:
            return Response({
                'message': 'Invalid update data',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    except User.DoesNotExist:
        return Response({
            'message': 'User not found'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([AllowAny])
def add_loyalty_points(request, id):
    """Add loyalty points endpoint matching Spring Boot /api/users/{id}/loyalty-points"""
    try:
        user = User.objects.get(id=id)
        serializer = AddLoyaltyPointsRequestSerializer(data=request.data)
        if serializer.is_valid():
            points = serializer.validated_data['points']
            user.loyalty_points += points
            user.save()  # This will automatically update loyalty_tier
            return Response(UserSerializer(user).data, status=status.HTTP_200_OK)
        else:
            return Response({
                'message': 'Invalid points data',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    except User.DoesNotExist:
        return Response({
            'message': 'User not found'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_email(request, id):
    """Verify email endpoint matching Spring Boot /api/users/{id}/verify-email"""
    try:
        user = User.objects.get(id=id)
        user.email_verified = True
        user.save()
        return Response(UserSerializer(user).data, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({
            'message': 'User not found'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([AllowAny])
def deactivate_user(request, id):
    """Deactivate user endpoint matching Spring Boot /api/users/{id}/deactivate"""
    try:
        user = User.objects.get(id=id)
        user.is_active = False
        user.save()
        return Response(UserSerializer(user).data, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({
            'message': 'User not found'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_users_by_loyalty_tier(request, tier):
    """Get users by loyalty tier endpoint matching Spring Boot /api/users/loyalty-tier/{tier}"""
    try:
        tier_upper = tier.upper()
        if tier_upper not in [choice[0] for choice in LoyaltyTier.choices]:
            return Response({
                'message': 'Invalid loyalty tier'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        users = User.objects.filter(loyalty_tier=tier_upper)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'message': f'Error retrieving users: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_active_users(request):
    """Get active users endpoint matching Spring Boot /api/users/active"""
    users = User.objects.filter(is_active=True)
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def check_user_exists(request, email):
    """Check if user exists endpoint matching Spring Boot /api/users/exists/{email}"""
    exists = User.objects.filter(email=email).exists()
    return Response({'exists': exists}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def user_health_check(request):
    """User service health check endpoint matching Spring Boot /api/users/health"""
    return Response({
        'status': 'UP',
        'service': 'User Service'
    }, status=status.HTTP_200_OK)

# ==================== POLL MANAGEMENT VIEWS ====================

@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_polls(request):
    """Get all active polls endpoint matching Spring Boot /api/polls"""
    polls = Poll.objects.filter(is_active=True)
    serializer = PollResponseSerializer(polls, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_poll_by_id(request, id):
    """Get poll by ID endpoint matching Spring Boot /api/polls/{id}"""
    try:
        poll = Poll.objects.get(id=id)
        serializer = PollResponseSerializer(poll)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Poll.DoesNotExist:
        return Response({
            'message': 'Poll not found'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([AllowAny])
def create_poll(request):
    """Create poll endpoint matching Spring Boot /api/polls"""
    serializer = CreatePollRequestSerializer(data=request.data)
    if serializer.is_valid():
        try:
            created_by_user = User.objects.get(id=serializer.validated_data['createdByUserId'])
            
            poll = Poll.objects.create(
                question=serializer.validated_data['question'],
                options=serializer.validated_data['options'],
                category=serializer.validated_data['category'],
                is_anonymous=serializer.validated_data['isAnonymous'],
                duration=serializer.validated_data.get('duration'),
                visibility=serializer.validated_data['visibility'],
                image_url=serializer.validated_data.get('imageUrl'),
                created_by=created_by_user
            )
            
            # Initialize votes dict with all options
            poll.votes = {option: 0 for option in poll.options}
            poll.save()
            
            return Response(PollResponseSerializer(poll).data, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response({
                'message': 'User not found'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'message': f'Failed to create poll: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({
        'message': 'Invalid poll data',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def vote_on_poll(request, id):
    """Vote on poll endpoint matching Spring Boot /api/polls/{id}/vote"""
    try:
        poll = Poll.objects.get(id=id)
        serializer = VoteRequestSerializer(data=request.data)
        
        if serializer.is_valid():
            option = serializer.validated_data['option']
            voter_user_id = serializer.validated_data['voterUserId']
            
            if option not in poll.options:
                return Response({
                    'message': 'Invalid option'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if user already voted
            if Vote.objects.filter(user_id=voter_user_id, poll=poll).exists():
                return Response({
                    'message': 'User has already voted on this poll'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create vote record
            Vote.objects.create(
                user_id=voter_user_id,
                poll=poll,
                option=option
            )
            
            # Update vote count
            if poll.votes is None:
                poll.votes = {}
            poll.votes[option] = poll.votes.get(option, 0) + 1
            poll.save()
            
            return Response(PollResponseSerializer(poll).data, status=status.HTTP_200_OK)
        else:
            return Response({
                'message': 'Invalid vote data',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    except Poll.DoesNotExist:
        return Response({
            'message': 'Poll not found'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_poll(request, id):
    """Delete poll endpoint matching Spring Boot /api/polls/{id}"""
    try:
        poll = Poll.objects.get(id=id)
        user_id = request.query_params.get('userId')
        
        if not user_id:
            return Response({
                'message': 'User ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user is the creator
        if poll.created_by.id != int(user_id):
            return Response({
                'message': 'Only poll creator can delete the poll'
            }, status=status.HTTP_403_FORBIDDEN)
        
        poll.delete()
        return Response({
            'message': 'Poll deleted successfully'
        }, status=status.HTTP_200_OK)
    except Poll.DoesNotExist:
        return Response({
            'message': 'Poll not found'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_polls_by_category(request, category):
    """Get polls by category endpoint matching Spring Boot /api/polls/category/{category}"""
    polls = Poll.objects.filter(category=category, is_active=True)
    serializer = PollResponseSerializer(polls, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_polls_by_user(request, userId):
    """Get polls by user endpoint matching Spring Boot /api/polls/user/{userId}"""
    polls = Poll.objects.filter(created_by_id=userId)
    serializer = PollResponseSerializer(polls, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_polls_by_visibility(request, visibility):
    """Get polls by visibility endpoint matching Spring Boot /api/polls/visibility/{visibility}"""
    try:
        visibility_upper = visibility.upper()
        if visibility_upper not in [choice[0] for choice in PollVisibility.choices]:
            return Response({
                'message': 'Invalid visibility setting'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        polls = Poll.objects.filter(visibility=visibility_upper, is_active=True)
        serializer = PollResponseSerializer(polls, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'message': f'Error retrieving polls: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_poll_statistics(request, id):
    """Get poll statistics endpoint matching Spring Boot /api/polls/{id}/statistics"""
    try:
        poll = Poll.objects.get(id=id)
        total_votes = poll.total_votes
        
        # Calculate option statistics
        option_stats = {}
        for option, votes in poll.votes.items():
            percentage = (votes / total_votes * 100) if total_votes > 0 else 0
            option_stats[option] = {
                'votes': votes,
                'percentage': round(percentage, 2)
            }
        
        # Calculate participation rate (simplified)
        participation_rate = min(total_votes / 100, 1.0) * 100  # Assume 100 is max expected votes
        
        stats = {
            'totalVotes': total_votes,
            'optionStats': option_stats,
            'participationRate': round(participation_rate, 2)
        }
        
        return Response(stats, status=status.HTTP_200_OK)
    except Poll.DoesNotExist:
        return Response({
            'message': 'Poll not found'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_available_categories(request):
    """Get available categories endpoint matching Spring Boot /api/polls/categories"""
    categories = Poll.objects.values_list('category', flat=True).distinct()
    return Response(list(categories), status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def polls_health_check(request):
    """Polls service health check endpoint matching Spring Boot /api/polls/health"""
    return Response({
        'status': 'UP',
        'service': 'Polls Service'
    }, status=status.HTTP_200_OK)

# ==================== LEGACY VIEWS (for backward compatibility) ====================

class PollViewSet(viewsets.ModelViewSet):
    queryset = Poll.objects.all()
    serializer_class = PollResponseSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        if not self.request.user.is_staff:
            raise PermissionDenied('Only admins can create polls.')
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        if not self.request.user.is_staff:
            raise PermissionDenied('Only admins can edit polls.')
        serializer.save()

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def results(self, request, pk=None):
        poll = self.get_object()
        serializer = self.get_serializer(poll)
        return Response(serializer.data)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class VoteViewSet(viewsets.ModelViewSet):
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user
        poll_id = request.data.get('poll')
        if Vote.objects.filter(user=user, poll_id=poll_id).exists():
            raise ValidationError('You have already voted in this poll.')
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

class UserProfileUpdateView(generics.UpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile

    def update(self, request, *args, **kwargs):
        user = request.user
        data = request.data
        # Update name (first_name) and email if present
        if 'name' in data:
            user.first_name = data['name']
        if 'email' in data:
            user.email = data['email']
        user.save()
        response = super().update(request, *args, **kwargs)
        # Add user info to the response data
        response.data['name'] = user.first_name
        response.data['email'] = user.email
        response.data['username'] = user.username
        return response
