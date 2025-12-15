from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Workspace


@admin.register(Workspace)
class WorkspaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'users_count')
    search_fields = ('name',)
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    def users_count(self, obj):
        return obj.users.count()
    users_count.short_description = 'Users Count'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'role', 'workspace', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active', 'is_staff', 'workspace')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('email',)
    readonly_fields = ('id', 'date_joined', 'last_login')
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('role', 'workspace')}),
    )
