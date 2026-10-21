
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from .forms import SignupForm, ReportForm, MessageForm, ClaimForm, FlagForm
from .matching import possible_matches
from .models import Report, Message, Claim, Notification, ReportFlag

def home(request):
    recent = Report.objects.filter(is_approved=True, status=Report.Status.OPEN).select_related("reporter")[:6]
    context = {
        "recent_reports": recent,
        "lost_count": Report.objects.filter(is_approved=True, kind=Report.Kind.LOST, status=Report.Status.OPEN).count(),
        "found_count": Report.objects.filter(is_approved=True, kind=Report.Kind.FOUND, status=Report.Status.OPEN).count(),
    }
    return render(request, "reports/home.html", context)

def signup(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = SignupForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Welcome to Findly! Your campus account is ready.")
        return redirect("dashboard")
    return render(request, "registration/signup.html", {"form": form})

def report_list(request):
    qs = Report.objects.filter(is_approved=True).exclude(status=Report.Status.ARCHIVED).select_related("reporter")
    q = request.GET.get("q", "").strip()
    kind = request.GET.get("kind", "")
    category = request.GET.get("category", "")
    location = request.GET.get("location", "").strip()
    date_from = request.GET.get("date_from", "")
    date_to = request.GET.get("date_to", "")
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q) | Q(location__icontains=q))
    if kind in dict(Report.Kind.choices):
        qs = qs.filter(kind=kind)
    if category in dict(Report.Category.choices):
        qs = qs.filter(category=category)
    if location:
        qs = qs.filter(location__icontains=location)
    if date_from:
        qs = qs.filter(item_date__gte=date_from)
    if date_to:
        qs = qs.filter(item_date__lte=date_to)
    return render(request, "reports/report_list.html", {
        "reports": qs, "q": q, "kind": kind, "category": category, "location": location,
        "date_from": date_from, "date_to": date_to, "categories": Report.Category.choices,
        "kinds": Report.Kind.choices,
    })

@login_required
def report_create(request):
    form = ReportForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        report = form.save(commit=False)
        report.reporter = request.user
        report.save()
        messages.success(request, "Your report is live. Findly is checking for possible matches.")
        for match in possible_matches(report, limit=3):
            Notification.objects.create(
                user=request.user, title="Possible match found",
                body=f"{match['report'].title} may match your report ({match['score']}% match score).",
                url=f"/reports/{report.pk}/matches/"
            )
        return redirect("report_detail", pk=report.pk)
    return render(request, "reports/report_form.html", {"form": form, "editing": False})

def report_detail(request, pk):
    report = get_object_or_404(Report.objects.select_related("reporter"), pk=pk, is_approved=True)
    if report.status == Report.Status.ARCHIVED and request.user != report.reporter and not request.user.is_staff:
        return redirect("report_list")
    messages_qs = Message.objects.filter(report=report).filter(Q(sender=request.user) | Q(recipient=request.user)) if request.user.is_authenticated else Message.objects.none()
    claim_form = ClaimForm()
    message_form = MessageForm()
    return render(request, "reports/report_detail.html", {
        "report": report, "claim_form": claim_form, "message_form": message_form,
        "thread_messages": messages_qs, "is_owner": request.user == report.reporter,
    })

@login_required
def report_edit(request, pk):
    report = get_object_or_404(Report, pk=pk)
    if report.reporter != request.user and not request.user.is_staff:
        return HttpResponseForbidden("You can only edit your own report.")
    form = ReportForm(request.POST or None, request.FILES or None, instance=report)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Report updated.")
        return redirect("report_detail", pk=report.pk)
    return render(request, "reports/report_form.html", {"form": form, "editing": True, "report": report})

@login_required
@require_POST
def report_status(request, pk):
    report = get_object_or_404(Report, pk=pk)
    if report.reporter != request.user and not request.user.is_staff:
        return HttpResponseForbidden("Only the reporter can update this status.")
    status = request.POST.get("status")
    if status not in [Report.Status.OPEN, Report.Status.RESOLVED, Report.Status.ARCHIVED]:
        return HttpResponseForbidden("Invalid status.")
    report.status = status
    report.save()
    if status == Report.Status.RESOLVED:
        for claim in report.claims.filter(status=Claim.Status.PENDING):
            claim.status = Claim.Status.DECLINED
            claim.save()
    messages.success(request, "Report status updated.")
    return redirect("report_detail", pk=pk)

@login_required
def matches(request, pk):
    report = get_object_or_404(Report, pk=pk, is_approved=True)
    if report.reporter != request.user and not request.user.is_staff:
        return HttpResponseForbidden("Possible matches are available to the report owner and staff.")
    return render(request, "reports/matches.html", {"report": report, "matches": possible_matches(report, limit=12)})

@login_required
@require_POST
def send_message(request, pk):
    report = get_object_or_404(Report, pk=pk, is_approved=True)
    if request.user == report.reporter:
        messages.error(request, "You cannot message yourself about your own report.")
        return redirect("report_detail", pk=pk)
    form = MessageForm(request.POST)
    if form.is_valid():
        msg = form.save(commit=False)
        msg.report = report
        msg.sender = request.user
        msg.recipient = report.reporter
        msg.save()
        Notification.objects.create(user=report.reporter, title="New private message", body=f"{request.user.first_name or request.user.username} sent you a message about {report.title}.", url=f"/reports/{report.pk}/")
        messages.success(request, "Your private message was sent.")
    else:
        messages.error(request, "Please enter a message of up to 1,200 characters.")
    return redirect("report_detail", pk=pk)

@login_required
@require_POST
def claim_create(request, pk):
    report = get_object_or_404(Report, pk=pk, is_approved=True)
    if report.reporter == request.user:
        messages.error(request, "You cannot claim your own report.")
        return redirect("report_detail", pk=pk)
    if report.status in [Report.Status.RESOLVED, Report.Status.ARCHIVED]:
        messages.error(request, "This report is no longer accepting claims.")
        return redirect("report_detail", pk=pk)
    form = ClaimForm(request.POST)
    if form.is_valid():
        claim, created = Claim.objects.get_or_create(report=report, claimant=request.user, defaults={"note": form.cleaned_data["note"]})
        if created:
            report.status = Report.Status.CLAIM_PENDING
            report.save()
            Notification.objects.create(user=report.reporter, title="Someone may have found their item", body=f"{request.user.first_name or request.user.username} submitted a claim for {report.title}.", url="/dashboard/")
            messages.success(request, "Claim sent privately to the reporter.")
        else:
            messages.info(request, "You have already submitted a claim for this report.")
    return redirect("report_detail", pk=pk)

@login_required
@require_POST
def claim_decision(request, pk, claim_id):
    claim = get_object_or_404(Claim, pk=claim_id, report_id=pk)
    if claim.report.reporter != request.user and not request.user.is_staff:
        return HttpResponseForbidden("Only the report owner can review claims.")
    decision = request.POST.get("decision")
    if decision not in [Claim.Status.ACCEPTED, Claim.Status.DECLINED]:
        return HttpResponseForbidden("Invalid decision.")
    claim.status = decision
    claim.save()
    if decision == Claim.Status.ACCEPTED:
        claim.report.status = Report.Status.RESOLVED
        claim.report.save()
        Notification.objects.create(user=claim.claimant, title="Claim accepted", body=f"Your claim for {claim.report.title} was accepted. Please coordinate privately.", url=f"/reports/{pk}/")
    else:
        Notification.objects.create(user=claim.claimant, title="Claim update", body=f"Your claim for {claim.report.title} was declined. You can message the reporter if you have more details.", url=f"/reports/{pk}/")
    messages.success(request, "Claim decision saved.")
    return redirect("report_detail", pk=pk)

@login_required
@require_POST
def flag_report(request, pk):
    report = get_object_or_404(Report, pk=pk)
    if report.reporter == request.user:
        messages.error(request, "You cannot flag your own report.")
        return redirect("report_detail", pk=pk)
    form = FlagForm(request.POST)
    if form.is_valid():
        flag, created = ReportFlag.objects.get_or_create(report=report, reporter=request.user, defaults={"reason": form.cleaned_data["reason"]})
        messages.success(request, "Thanks — campus staff can review this report." if created else "You have already flagged this report.")
    return redirect("report_detail", pk=pk)

@login_required
def dashboard(request):
    my_reports = Report.objects.filter(reporter=request.user).order_by("-created_at")
    received_messages = Message.objects.filter(recipient=request.user).select_related("sender", "report")
    sent_messages = Message.objects.filter(sender=request.user).select_related("recipient", "report")
    claims_made = Claim.objects.filter(claimant=request.user).select_related("report")
    claims_received = Claim.objects.filter(report__reporter=request.user).select_related("claimant", "report")
    notifications = request.user.findly_notifications.all()[:12]
    unread_count = request.user.findly_notifications.filter(is_read=False).count()
    return render(request, "reports/dashboard.html", {
        "my_reports": my_reports, "received_messages": received_messages[:8],
        "sent_messages": sent_messages[:8], "claims_made": claims_made,
        "claims_received": claims_received, "notifications": notifications,
        "unread_count": unread_count,
    })

@login_required
@require_POST
def notification_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save(update_fields=["is_read"])
    return redirect(notification.url or "dashboard")
