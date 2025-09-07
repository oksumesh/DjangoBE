from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Poll, Vote, UserProfile, User

# Custom User Admin
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_active', 'email_verified', 'loyalty_tier', 'loyalty_points', 'created_at')
    list_filter = ('is_active', 'email_verified', 'loyalty_tier', 'created_at')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone_number')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('RedCurtains Fields', {'fields': ('email_verified', 'loyalty_points', 'loyalty_tier', 'last_login_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )

class PollAdmin(admin.ModelAdmin):
    list_display = ('question', 'category', 'is_active', 'visibility', 'created_by', 'created_at')
    list_filter = ('is_active', 'visibility', 'category', 'created_at')
    search_fields = ('question', 'category', 'created_by__email')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (None, {'fields': ('question', 'category', 'created_by')}),
        ('Options & Votes', {'fields': ('options', 'votes')}),
        ('Settings', {'fields': ('is_active', 'is_anonymous', 'visibility', 'duration', 'image_url')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

class VoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'poll', 'option', 'timestamp')
    list_filter = ('timestamp', 'poll__category')
    search_fields = ('user__email', 'poll__question', 'option')

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'is_verified')
    search_fields = ('user__email', 'phone')

# Register models
admin.site.register(User, CustomUserAdmin)
admin.site.register(Poll, PollAdmin)
admin.site.register(Vote, VoteAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
