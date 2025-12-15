from django.contrib import admin
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'priority', 'created_by', 'created_by_ai', 'created_at']
    list_filter = ['status', 'priority', 'created_by_ai']
    search_fields = ['title', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']
