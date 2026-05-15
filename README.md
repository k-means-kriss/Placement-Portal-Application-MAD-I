# 🎓 Placement Portal Application — MAD-I

> **Modern Application Development I | IIT Madras BS in Data Science & Applications**

A full-stack web application built with **Flask** and **SQLite** that connects students, companies, and administrators for managing placement drives, job postings, and applications — all in one place.

---

## 🚀 Live Demo / Repo

🔗 [GitHub Repository](https://github.com/k-means-kriss/Placement-Portal-Application-MAD-I)

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Python, Flask |
| **Database** | SQLite |
| **Frontend** | HTML, CSS, Bootstrap, Jinja2 |
| **Auth** | Flask-Login, Session Management |
| **Version Control** | Git & GitHub |

---

## 📁 Project Structure

```
Placement-Portal-Application-MAD-I/
├── app.py                  # Flask routes and application logic
├── model.py                # SQLite database functions & schema
├── requirements.txt        # Python dependencies
├── README.md
├── .gitignore
├── static/
│   ├── css/                # Stylesheets
│   └── uploads/
│       └── resumes/        # Uploaded student resumes
├── templates/
│   ├── admin/              # Admin dashboard templates
│   ├── company/            # Company dashboard templates
│   └── student/            # Student dashboard templates
└── instance/
    └── database.db         # SQLite database file
```

---

## 👥 Roles & Access

| Role | Description |
|------|-------------|
| 🔑 **Admin** | Predefined user. Approves companies, manages all platform data |
| 🏢 **Company** | Self-registers, posts jobs after admin approval |
| 🎓 **Student** | Self-registers, builds profile, applies to job postings |

---

## ✨ Features

### Admin
- Approve or reject company registrations
- View and manage all students, companies, and applications
- Monitor placement statistics

### Company
- Register and log in
- Post placement drives / job listings (after admin approval)
- View applications received from students

### Student
- Register and log in
- Build a profile with resume upload
- Browse approved job listings
- Apply to placement drives
- Track application status

---

## ⚙️ How to Run Locally

```bash
# 1. Clone the repository
git clone https://github.com/k-means-kriss/Placement-Portal-Application-MAD-I.git
cd Placement-Portal-Application-MAD-I

# 2. Create and activate a virtual environment (recommended)
python3 -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python app.py
```

Visit **`http://127.0.0.1:8000`** in your browser.

---

## 🔐 Default Admin Credentials

| Field | Value |
|-------|-------|
| Email | `admin123@gmail.com` |
| Password | `admin123#` |

> ⚠️ Change these credentials before deploying to production.

---

## 📦 Important Notes

- Data is stored in `instance/database.db` (SQLite)
- Uploaded resumes are saved under `static/uploads/resumes/`
- For production deployment, set a secure `SECRET_KEY` environment variable:
  ```bash
  export SECRET_KEY="your-secure-random-key"
  ```

---

## 🏁 Milestone Progress

| Milestone | Description | Status |
|-----------|-------------|--------|
| Milestone 0 | GitHub Repository Setup | ✅ Done |
| Milestone 1 | Database Models & Schema | ✅ Done |
| Milestone 2 | Authentication & RBAC | ✅ Done |
| Milestone 3 | Admin Dashboard & Management | ✅ Done |
| Milestone 4 | Company Dashboard & Management | ✅ Done |
| Milestone 5 | Student Dashboard & Management | ✅ Done |
| Milestone 6 | Placement Status Tracking | ✅ Done |

### 🌟 Optional Enhancements

| Enhancement | Status |
|-------------|--------|
| REST API Integration | ✅ Done |
| Charts & Data Visualization | ✅ Done |
| Frontend & Backend Validation | ✅ Done |
| Responsive UI & Styling | ✅ Done |
| Flask-Login & Security Hardening | ✅ Done |

---

## 📊 Project Result

| Metric | Value |
|--------|-------|
| **Course** | Modern Application Development I (MAD-I) |
| **Programme** | IIT Madras BS in Data Science & Applications |
| **Score** | 90 / 100 |
| **Grade** | S |

---

## 📄 License

This project was built for academic purposes as part of the IIT Madras BS programme.

---

*Made with ❤️ as part of the IIT Madras BS in Data Science & Applications programme.*
