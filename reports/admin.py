
from django.contrib import admin
from .models import Report, Message, Claim, Notification, ReportFlag

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("title", "kind", "category", "location", "reporter", "status", "is_approved", "created_at")
    list_filter = ("kind", "category", "status", "is_approved")
    search_fields = ("title", "description", "location", "reporter__username", "reporter__email")
    list_editable = ("is_approved", "status")
    readonly_fields = ("created_at", "updated_at")

@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = ("report", "claimant", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("report__title", "claimant__username")

@admin.register(ReportFlag)
class ReportFlagAdmin(admin.ModelAdmin):
    list_display = ("report", "reporter", "reason", "reviewed", "created_at")
    list_filter = ("reviewed",)
    list_editable = ("reviewed",)
    search_fields = ("report__title", "reason")

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("report", "sender", "recipient", "created_at", "is_read")
    readonly_fields = ("created_at",)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "title", "is_read", "created_at")
    list_filter = ("is_read",)
