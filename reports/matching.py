
from datetime import timedelta
from django.db.models import Q
from .models import Report

def score_match(source, candidate):
    """Explainable heuristic score; returns (score, reasons)."""
    if source.pk == candidate.pk or source.kind == candidate.kind:
        return 0, []
    if source.status in [Report.Status.RESOLVED, Report.Status.ARCHIVED] or candidate.status in [Report.Status.RESOLVED, Report.Status.ARCHIVED]:
        return 0, []
    score, reasons = 0, []
    if source.category == candidate.category:
        score += 35
        reasons.append("same category")
    source_words = set((source.title + " " + source.description).lower().split())
    candidate_words = set((candidate.title + " " + candidate.description).lower().split())
    stop = {"the","and","with","from","this","that","have","was","were","for","item","found","lost","near","its","has","are","not"}
    overlap = source_words.intersection(candidate_words) - stop
    if overlap:
        points = min(30, len(overlap) * 7)
        score += points
        reasons.append("shared details: " + ", ".join(sorted(overlap)[:4]))
    if source.location.lower().split("-")[0].strip() == candidate.location.lower().split("-")[0].strip():
        score += 20
        reasons.append("similar campus location")
    elif source.location.lower() in candidate.location.lower() or candidate.location.lower() in source.location.lower():
        score += 12
        reasons.append("overlapping location")
    delta = abs((source.item_date - candidate.item_date).days)
    if delta == 0:
        score += 15
        reasons.append("same date")
    elif delta <= 2:
        score += 10
        reasons.append("within 2 days")
    elif delta <= 7:
        score += 5
        reasons.append("within a week")
    return min(score, 100), reasons

def possible_matches(report, limit=6):
    candidates = Report.objects.filter(is_approved=True).exclude(pk=report.pk).exclude(status__in=[Report.Status.RESOLVED, Report.Status.ARCHIVED]).filter(~Q(reporter=report.reporter) | Q(reporter=report.reporter))
    ranked = []
    for candidate in candidates[:300]:
        score, reasons = score_match(report, candidate)
        if score >= 20:
            ranked.append({"report": candidate, "score": score, "reasons": reasons})
    return sorted(ranked, key=lambda x: (-x["score"], x["report"].created_at))[:limit]
