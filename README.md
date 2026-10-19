# 🩸 BloodLink — Blood Donor Finder System

A Django web app connecting **donors, hospitals and health organizations** for
emergency blood needs — with donor search, emergency requests + auto-matching,
donation camps, a rewards/badge system, notifications, and admin analytics.

---

## 🚀 Quick Start

### Easiest — Windows one-click
Just **double-click `start.bat`**. The first time it automatically creates the
environment, installs everything, sets up the database and loads demo data; after
that it detects the existing environment and launches the app directly, opening
your browser at http://127.0.0.1:8000.

### Manual (any OS)
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py seed          # loads demo data (badges, donors, hospitals, orgs)
python manage.py runserver
```

Open **http://127.0.0.1:8000/**

### Demo accounts (from `seed`)

| Role | Username | Password | Notes |
|------|----------|----------|-------|
| Admin | `admin` | `admin12345` | approvals + analytics |
| Hospital (approved) | `hospital1` | `hospital12345` | can raise requests |
| Hospital (pending) | `hospital2` | `hospital12345` | awaiting admin approval |
| Organization (approved) | `org1` | `org12345` | can run camps |
| Organization (pending) | `org2` | `org12345` | awaiting admin approval |
| Donors | `donor1` … `donor16` | `donor12345` | |

---

## ✨ Latest feature updates

**1. Admin approval for hospitals & organizations**
New hospital/organization accounts start **Pending** and must be approved by an
admin (Admin → Dashboard → **Approvals**) before they can operate. Donors
self-register and get access immediately. Approval also sets the account's
**Verified ✓** flag.

**2. Login-required donor search (privacy)**
"Find Donors" and donor contact pages now require login, so donor names and
contact details are never public.

**3. Donation certificate upload + approval (proof)**
Donors upload a **photo/PDF certificate** (Donation History → *Upload
Certificate*). It stays **Pending** until an admin or hospital approves it
(Admin/Hospital → **Certificates**). Only **approved** certificates add a
verified donation and award points/badges.

**4. Email contact + email alerts**
The donor page now has an **Email** button (replaces Call). When a hospital
raises a request, matched donors also receive an **emergency email** in addition
to the in-app alert. See *Email setup* below.

**5. Two-way notification system**
- Hospital gets a **"request sent to N donors"** confirmation.
- Matched donors get the emergency alert and an **"I can donate / Can't right now"** button.
- When a donor accepts, the **hospital is notified** (in-app + email) with the donor's contact.
- The responding donor gets a **thank-you** notification.
- The hospital's request page shows a **responders list** with contact details.

---

## 📧 Email setup (Gmail SMTP)

Emails work out of the box using the **console backend** (messages print to the
terminal) — no setup needed for a demo.

To send **real emails via Gmail**, add your credentials in `config/settings.py`
(or as environment variables `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD`):

```python
EMAIL_HOST_USER = "yourname@gmail.com"
EMAIL_HOST_PASSWORD = "abcd efgh ijkl mnop"   # 16-char Gmail App Password
```

Get an App Password at **Google Account → Security → 2-Step Verification → App
passwords**. With both values set, BloodLink switches to Gmail SMTP
automatically; leave them blank to keep the console backend.

---

## 🗂️ Tech
- Django 6.1 · SQLite (swap `DATABASES` in `config/settings.py` for Postgres/MySQL)
- Custom role-based User model · media uploads for certificates
- Vanilla animated CSS + Font Awesome (no build step)

## ⚠️ Production notes
- Set `DEBUG = False`, change `SECRET_KEY`, configure `ALLOWED_HOSTS`
- Run `python manage.py collectstatic`
- Serve `MEDIA_ROOT` (uploaded certificates) via your web server
