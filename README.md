
# Findly — Campus Lost & Found Hub

A college-only lost-and-found portal built with Django. Students can report lost/found items, browse and filter reports, see possible matches, privately contact the reporter, and follow the status of their reports. Staff can moderate listings through Django Admin.

## Features
- College email-domain validation (configure `COLLEGE_EMAIL_DOMAIN` in `findly/settings.py`)
- Optional shared campus invite code (`COLLEGE_INVITE_CODE`)
- Sign up, login, logout, profile and personal dashboard
- Lost/found reports with photo uploads, category, location, date, description and status
- Search and filters for keyword, category, report type, location and date
- Matching suggestions based on category, keywords, location and date proximity
- Private in-app messages; email/phone details are not published on report cards
- Claim/return workflow, status updates, and resolution tracking
- In-app notifications for new messages, match suggestions and report status changes
- Report helpfulness/flagging and staff moderation through Django Admin
- Responsive, accessible UI with mobile navigation and empty states
- Django CSRF protection, server-side form validation and upload type/size checks

## Quick start
Python 3.10+ recommended.

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure college access
# Edit findly_project/settings.py:
# COLLEGE_EMAIL_DOMAIN = "yourcollege.edu"
# Optionally set COLLEGE_INVITE_CODE = "your-campus-code"

# 4. Create the database and admin account
python manage.py migrate --run-syncdb
python manage.py createsuperuser

# 5. Run locally
python manage.py runserver
```
Open http://127.0.0.1:8000/

## College-only access
By default, registration accepts addresses ending in `@college.edu`. Change `COLLEGE_EMAIL_DOMAIN` to your real campus domain before use. If students use multiple approved domains, update `SignupForm.clean_email()` to check an allow-list. An optional invite code can further restrict registration. This is an application-level gate, not a substitute for campus SSO in a production deployment.

## Demo flow
1. Register two test users with addresses on your configured domain.
2. Create a LOST report as one user and a FOUND report with similar category/keywords/location as the other.
3. Open a report and use **Possible matches** to review candidate reports.
4. Send a private message or submit a claim request.
5. Visit **My dashboard** to manage your reports and see notifications.
6. Use `/admin/` to moderate reports and review flags.

## Notes before production
- Set a strong `SECRET_KEY`, `DEBUG=False`, and proper `ALLOWED_HOSTS`.
- Configure HTTPS, secure cookies, database backups, media storage and email delivery.
- Use a real campus SSO or verified email flow if identity assurance is required.
- The included matching system is explainable rule-based scoring, not machine learning.
- The default database is SQLite for easy student-project setup. PostgreSQL is recommended for deployment.
