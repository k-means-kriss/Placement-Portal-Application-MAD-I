<<<<<<< HEAD
# Placement Portal Application — MAD-I

> Modern Application Development I | IIT Madras BS Programme

A web-based Placement Portal built with Flask and SQLite that connects students, companies, and administrators for managing job postings, applications, and placement drives.

---

## Tech Stack

- **Backend:** Python, Flask
- **Database:** SQLite
- **Frontend:** HTML, CSS, Bootstrap, Jinja2
- **Version Control:** Git & GitHub

---

## Project Structure

```
placement-portal-mad1/
├── app.py
├── models.py
├── README.md
├── .gitignore
├── static/
│   └── css/
├── templates/
│   ├── admin/
│   ├── company/
│   └── student/
└── instance/
    └── placement.db
```

---

## Roles

| Role | Description |
|------|-------------|
| **Admin** | Predefined. Approves companies, manages all data |
| **Company** | Registers, posts jobs after admin approval |
| **Student** | Registers, applies to approved job postings |

---

## Milestone Progress

| Milestone | Commit Message | Status |
|-----------|----------------|--------|
| GitHub Repository Setup | `Milestone-0 PPA-MAD-1` | ✅ Done |
| Database Models & Schema | `Milestone-PPA DB-Relationship` | ⬜ Pending |
| Authentication & RBAC | `Milestone-PPA Auth_RBAC` | ⬜ Pending |
| Admin Dashboard | `Milestone-PPA Admin-Dashboard-Management` | ⬜ Pending |
| Company Dashboard | `Milestone-PPA Company-Dashboard-Management` | ⬜ Pending |
| Student Dashboard | `Milestone-PPA Student-Dashboard-Management` | ⬜ Pending |
| Placement Status Tracking | `Milestone-PPA Placement-Tracking` | ⬜ Pending |

---

## Optional Enhancements

| Milestone | Commit Message |
|-----------|----------------|
| API Integration | `Milestone-PPA Created-API` |
| Charts & Visualization | `Milestone-PPA Charts` |
| Frontend & Backend Validation | `Milestone-PPA Validation` |
| Responsive UI & Styling | `Milestone-PPA Responsive-UI` |
| Flask-Login & Security | `Milestone-PPA Flask-Integration` |

---

## How to Run Locally

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/placement-portal-mad1.git
cd placement-portal-mad1

# 2. Install dependencies
pip install flask

# 3. Run the app
python app.py
```

Visit `http://localhost:5000` in your browser.

---

## Issues & Notes

Track issues and blockers in the [GitHub Issues](../../issues) tab.

---

*Project submitted as part of the IIT Madras BS in Data Science & Applications programme.*
=======
# Placement Website Project

This is a simple placement website made using Flask and SQLite.
It has 3 main users:
- Admin
- Company
- Student

## Main Features
- Company registration and login
- Student registration and login
- Admin approval and management
- Placement drive creation and applications
- Resume upload for student profile

## Tech Used
- Python
- Flask
- SQLite
- HTML/CSS

## How to Run
1. Open terminal in project folder.
2. Create virtual env (optional but recommended):
   - `python3 -m venv .venv`
3. Activate env:
   - macOS/Linux: `source .venv/bin/activate`
4. Install dependencies:
   - `pip install -r requirements.txt`
5. Run app:
   - `python app.py`
6. Open browser:
   - `http://127.0.0.1:8000`

## Default Admin Login
- Email: admin123@gmail.com
- Password: admin123#

## Important Notes
- This project stores data in `database.db`.
- Uploaded resumes are saved in `static/uploads/resumes`.
- For production, set environment variable `SECRET_KEY`.

## Project Folder Structure (basic)
- `app.py` -> Flask routes and app logic
- `model.py` -> SQLite database functions
- `templates/` -> HTML pages
- `static/` -> CSS and uploaded files
- `requirements.txt` -> Python dependencies
- `.gitignore` -> files/folders ignored in git
>>>>>>> 4985b2f (Milestone-PPA DB-Relationship)
