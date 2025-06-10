from rest_framework.routers import DefaultRouter
from .views import PollViewSet, OptionViewSet, VoteViewSet, UserViewSet, RegisterView, LoginView, UserProfileUpdateView
from django.urls import path, include

router = DefaultRouter()
router.register(r'polls', PollViewSet)
router.register(r'options', OptionViewSet)
router.register(r'votes', VoteViewSet)
router.register(r'users', UserViewSet)

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('profile/', UserProfileUpdateView.as_view(), name='profile-update'),
    path('polls/<int:pk>/results/', PollViewSet.as_view({'get': 'results'}), name='poll-results'),
    path('', include(router.urls)),
] 