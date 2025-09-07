from rest_framework.routers import DefaultRouter
from .views import (
    # Authentication views
    register, login, refresh_token, logout, forgot_password, verify_otp, reset_password, google_auth,
    # User management views
    get_all_users, get_user_by_id, get_user_by_email, create_user, update_user,
    add_loyalty_points, verify_email, deactivate_user, get_users_by_loyalty_tier,
    get_active_users, check_user_exists, user_health_check,
    # Poll management views
    get_all_polls, get_poll_by_id, create_poll, vote_on_poll, delete_poll,
    get_polls_by_category, get_polls_by_user, get_polls_by_visibility,
    get_poll_statistics, get_available_categories, polls_health_check,
    # Legacy viewsets
    PollViewSet, VoteViewSet, UserViewSet, UserProfileUpdateView
)
from django.urls import path, include

# Legacy router for backward compatibility
router = DefaultRouter()
# Note: Removed 'polls' registration to avoid conflicts with /api/polls/* routes
router.register(r'votes', VoteViewSet)
router.register(r'users', UserViewSet)

urlpatterns = [
    # ==================== AUTHENTICATION ROUTES ====================
    # Matching Spring Boot /api/auth/* routes
    path('auth/register/', register, name='register'),
    path('auth/login/', login, name='login'),
    path('auth/refresh/', refresh_token, name='refresh-token'),
    path('auth/logout/', logout, name='logout'),
    path('auth/forgot/', forgot_password, name='forgot-password'),
    path('auth/verify-otp/', verify_otp, name='verify-otp'),
    path('auth/reset-password/', reset_password, name='reset-password'),
    path('auth/google/', google_auth, name='google-auth'),
    
    # ==================== USER MANAGEMENT ROUTES ====================
    # Matching Spring Boot /api/users/* routes
    path('users/', get_all_users, name='get-all-users'),
    path('users/<int:id>/', get_user_by_id, name='get-user-by-id'),
    path('users/email/<str:email>/', get_user_by_email, name='get-user-by-email'),
    path('users/create/', create_user, name='create-user'),
    path('users/<int:id>/update/', update_user, name='update-user'),
    path('users/<int:id>/loyalty-points/', add_loyalty_points, name='add-loyalty-points'),
    path('users/<int:id>/verify-email/', verify_email, name='verify-email'),
    path('users/<int:id>/deactivate/', deactivate_user, name='deactivate-user'),
    path('users/loyalty-tier/<str:tier>/', get_users_by_loyalty_tier, name='get-users-by-loyalty-tier'),
    path('users/active/', get_active_users, name='get-active-users'),
    path('users/exists/<str:email>/', check_user_exists, name='check-user-exists'),
    path('users/health/', user_health_check, name='user-health-check'),
    
    # ==================== POLL MANAGEMENT ROUTES ====================
    # Matching Spring Boot /api/polls/* routes
    path('polls/', get_all_polls, name='get-all-polls'),
    path('polls/<int:id>/', get_poll_by_id, name='get-poll-by-id'),
    path('polls/create/', create_poll, name='create-poll'),
    path('polls/<int:id>/vote/', vote_on_poll, name='vote-on-poll'),
    path('polls/<int:id>/delete/', delete_poll, name='delete-poll'),
    path('polls/category/<str:category>/', get_polls_by_category, name='get-polls-by-category'),
    path('polls/user/<int:userId>/', get_polls_by_user, name='get-polls-by-user'),
    path('polls/visibility/<str:visibility>/', get_polls_by_visibility, name='get-polls-by-visibility'),
    path('polls/<int:id>/statistics/', get_poll_statistics, name='get-poll-statistics'),
    path('polls/categories/', get_available_categories, name='get-available-categories'),
    path('polls/health/', polls_health_check, name='polls-health-check'),
    
    # ==================== LEGACY ROUTES (for backward compatibility) ====================
    path('legacy/auth/register/', register, name='legacy-register'),
    path('legacy/auth/login/', login, name='legacy-login'),
    path('legacy/profile/', UserProfileUpdateView.as_view(), name='profile-update'),
    path('legacy/polls/<int:pk>/results/', PollViewSet.as_view({'get': 'results'}), name='poll-results'),
    # Note: Legacy router moved to end to avoid conflicts with specific API routes
    path('legacy/', include(router.urls)),
] 