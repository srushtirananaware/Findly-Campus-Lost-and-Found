
from django.conf import settings
from django.db import models
from django.utils import timezone

class Report(models.Model):
    class Kind(models.TextChoices):
        LOST = "LOST", "Lost"
        FOUND = "FOUND", "Found"

    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        CLAIM_PENDING = "CLAIM_PENDING", "Claim pending"
        RESOLVED = "RESOLVED", "Resolved"
        ARCHIVED = "ARCHIVED", "Archived"

    class Category(models.TextChoices):
        ELECTRONICS = "Electronics", "Electronics"
        ID_CARDS = "ID cards", "ID cards"
        BOOKS = "Books & notes", "Books & notes"
        BAGS = "Bags & wallets", "Bags & wallets"
        KEYS = "Keys", "Keys"
        CLOTHING = "Clothing", "Clothing"
        ACCESSORIES = "Accessories", "Accessories"
        STATIONERY = "Stationery", "Stationery"
        OTHER = "Other", "Other"

    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reports")
    kind = models.CharField(max_length=5, choices=Kind.choices)
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=1500)
    category = models.CharField(max_length=30, choices=Category.choices)
    location = models.CharField(max_length=120, help_text="Campus location, e.g. Library - 2nd floor")
    item_date = models.DateField(help_text="Date the item was lost or found")
    photo = models.ImageField(upload_to="report_photos/%Y/%m/", blank=True, null=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_kind_display()}: {self.title}"

    @property
    def is_open(self):
        return self.status in [self.Status.OPEN, self.Status.CLAIM_PENDING]


class Message(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_findly_messages")
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="received_findly_messages")
    body = models.TextField(max_length=1200)
    created_at = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Message on {self.report_id} from {self.sender}"


class Claim(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        ACCEPTED = "ACCEPTED", "Accepted"
        DECLINED = "DECLINED", "Declined"

    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name="claims")
    claimant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="claims_made")
    note = models.CharField(max_length=500)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]
        constraints = [models.UniqueConstraint(fields=["report", "claimant"], name="one_claim_per_user_report")]


class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="findly_notifications")
    title = models.CharField(max_length=120)
    body = models.CharField(max_length=280)
    url = models.CharField(max_length=240, default="/dashboard/")
    created_at = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class ReportFlag(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name="flags")
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="findly_flags")
    reason = models.CharField(max_length=300)
    created_at = models.DateTimeField(default=timezone.now)
    reviewed = models.BooleanField(default=False)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["report", "reporter"], name="one_flag_per_user_report")]
