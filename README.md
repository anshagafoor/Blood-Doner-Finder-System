# 🩸 Blood Donor Finder System

A full-featured, modern web platform connecting voluntary blood donors, healthcare facilities, and charity organizations to streamline life-saving blood donations.

---

## 🌟 Key Features

### 👤 Role-Based Portals
- **Donors**: Search and connect with requests, view donation history, track eligibility cooldowns, and view rewards.
- **Hospitals**: Post emergency and standard blood requests, track real-time fulfillment, and locate matching donors by blood group compatibility.
- **Organizations**: Schedule and coordinate blood donation camps and community awareness drives.
- **Administrators**: Centralized dashboard to oversee hospital/organization verifications, camp approvals, and platform metrics.

### 🩸 Intelligent Compatibility & Matching
- Real-time blood group compatibility matching matrix (ABO and Rh factor).
- Proximity and availability filtering for rapid donor discovery.

### 🏆 Gamification & Rewards
- Donor badges, point accumulation for verified donations, and public leaderboards to encourage voluntary giving.

### 🔔 Real-Time Notification System
- Immediate alerts for urgent requests and camp invitations with global unread badge counters.

---

## 🚀 Quick Start & Installation

### 1. Prerequisites
- Python 3.10+
- Virtual environment (`venv`)

### 2. Setup Virtual Environment
```bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup & Seeding
```bash
python manage.py migrate
python manage.py seed
```
> The `seed` command initializes sample users across all roles (Donor, Hospital, Organization, Admin) with dummy camps, requests, and rewards for instant testing.

### 5. Run Local Server
```bash
python manage.py runserver
```
Navigate to `http://127.0.0.1:8000` in your web browser.

---

## 📁 Project Architecture

```
blood_donor_finder/
├── accounts/          # User authentication, roles, custom user model, and permissions
├── config/            # Django project settings, root URLs, ASGI, and WSGI entrypoints
├── core/              # Landing page, unified dashboards, and management seed commands
├── donors/            # Donor profiles, search filters, and donation history
├── hospitals/         # Hospital profiles and emergency blood request management
├── notifications/     # Notification models, context processors, and alert views
├── organizations/     # Camp coordination and awareness drive management
├── rewards/           # Gamification points, badges, services, and leaderboards
├── static/            # CSS stylesheets and interactive JavaScript
└── templates/         # HTML5 templates with clean modular inheritance
```

---

## 🧪 Running Tests
```bash
python manage.py test
```

---

## 📄 License
This project is open-source and available under the MIT License.
