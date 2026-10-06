# Shani Glorious Day Care Centre

A Django website and staff workspace for Shani Glorious Day Care Centre, Ipuli Ward, Tabora, Tanzania.

## Run locally

Python 3.13 or newer is recommended.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open `http://127.0.0.1:8000/` for the public website. Staff sign in at `/staff/login/`; Django's full record manager is at `/admin/`. Use the superuser created above to access both staff areas.

## Centre workspace

- Public centre profile, programmes, announcements, upcoming events, and admission enquiries.
- Staff dashboard with child, enquiry, attendance, and outstanding-fee summaries.
- Child and family records with optional child photos and allergy notes.
- Daily attendance register with present, absent, late, and excused states.
- Fee records with due dates, amounts paid, balances, and overdue status.
- Enquiry follow-up stages, centre announcements, calendar events, staff directory, and care notes in the staff workspace/admin.

Enquiries are stored in the database and can be followed up from the staff workspace. Announcements, events, staff members, and care notes are managed in Django admin.

## Before deployment

This is configured for local development with SQLite and `DJANGO_DEBUG = true`. Before publishing, set a private `DJANGO_SECRET_KEY`, set `DJANGO_DEBUG=false`, configure `DJANGO_ALLOWED_HOSTS` and HTTPS/CSRF settings, choose a production database, configure email delivery, and use persistent media storage and static-file hosting. Do not use the development server as a public production server.

The centre has not provided a public phone number, so the site uses the supplied email and address rather than inventing one.
