# 🎓 E-Learning Platform (LMS) - Desktop Application

A comprehensive **Learning Management System** built with **Python** and **PyQt5**, featuring role-based access control, course management, lecture delivery (PDF viewer), quiz system, and real-time statistics.

---

## ☰ Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Usage](#-usage)
- [Database Schema](#-database-schema)
- [Key Modules](#-key-modules)
- [Screenshots](#-screenshots)
- [License](#-license)
- [Support](#-support)

---

## ✨ Features

### 🔐 Authentication & Authorization
- **Secure Login/Register** with email & password
- **Role-based access**: Student / Admin
- **Password hashing** using PBKDF2-SHA256 (600,000 iterations)
- **Session management** with SQLite backend

### 👨‍🎓 Student Features
- **Course Enrollment** - Browse and enroll in available courses
- **Lecture Viewer** - Read PDF lectures with page navigation (PyMuPDF + QtWebEngine)
- **Quiz System** - Take timed quizzes with multiple question types
- **Progress Tracking** - View quiz statistics and performance history
- **Responsive UI** - Modern, clean interface with icons and animations

### 👨‍🏫 Admin Features
- **Course Management** - Create, edit, delete courses with categories
- **Lecture Management** - Upload PDF lectures per course
- **Quiz Creation** - Build quizzes with questions and answers
- **Analytics Dashboard** - View quiz statistics across all students
- **User Management** - Overview of enrolled students

### ✒️ UI/UX Highlights
- **Custom styling** with QSS (Qt Style Sheets)
- **Animated sidebar** with collapsible menu
- **Background images** with rounded corners and shadows
- **Icon integration** via `qtawesome` (FontAwesome)
- **Greek language support** throughout the interface

---

## 🛠 Tech Stack

| Category | Technology |
|----------|------------|
| **Language** | Python 3.8+ |
| **GUI Framework** | PyQt5 (≥5.15.0) |
| **Web Engine** | PyQtWebEngine (≥5.15.0) |
| **PDF Rendering** | PyMuPDF (fitz) (≥1.23.0) |
| **Icons** | qtawesome (≥1.2.0) |
| **Charts** | matplotlib (≥3.7.0) |
| **Database** | SQLite3 (built-in) |
| **Security** | hashlib, hmac, secrets (stdlib) |

---

## 📁 Project Structure

```
LMS-PROJECT-Σχολή/
│
├── 📄 Main Application Files
│   ├── main_window.py              # Entry point, login/landing screen
│   ├── login_window.py             # Login form with validation
│   ├── register_window.py          # Registration form
│   ├── course_management_window.py # Main dashboard (student/admin)
│   ├── db.py                       # Database layer (SQLite + password hashing)
│   ├── requirements.txt            # Python dependencies
│   └── table_with_background.py    # Utility for styled tables
│
├── 📁 course_management_logic.py   # Business logic for course management
├── 📁 course_management_pages.py   # UI pages for course management
│
├── 📁 admin_functions/
│   └── admin_total_quiz_widget.py  # Admin quiz statistics dashboard
│
├── 📁 lectures_functions/
│   └── lectures_functions.py       # PDF lecture viewer (PyMuPDF + WebEngine)
│
├── 📁 quiz_functions/
│   ├── quiz_selectiondialog.py     # Admin: select course for quiz creation
│   └── quiz_execution_dialog.py    # Student: take quiz interface
│
├── 📁 student_functions/
│   ├── student_quiz_selection_dialog.py  # Student: browse & start quizzes
│   └── student_quiz_stats_page.py        # Student: quiz statistics view
│
├── 📁 subjects_interface/
│   └── subjects_available_interface.py   # Course enrollment page
│
├── 📁 styles_css/
│   └── styles.py                   # Centralized QSS stylesheets
│
└── 📁 icons/                       # Application icons & images
    ├── background-main-window.png
    ├── left_panel_icon_bg.png
    ├── icon-main-window.png
    ├── menu.png
    ├── lectures.png
    ├── quiz-list-book.png
    ├── quiz-exam.png
    ├── online-test-title.png
    ├── help-icon.png
    ├── education.png
    ├── online-test.png
    ├── email-icon.png
    ├── eye_open.png
    ├── eye_close.png
    ├── login-icon.png
    ├── name-icon.png
    ├── close-window.png
    ├── previous-page.png
    ├── next-page.png
    └── ... (other icons)
```

---

## Installation

### Prerequisites
- **Python 3.8 or higher**
- **pip** (Python package manager)

### Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd LMS-PROJECT-Σχολή
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python main_window.py
   ```

> **Note**: On first run, the SQLite database (`lms.db`) will be automatically created with the required tables.

---

## Usage

### First Time Setup 
1. Launch the application: `python main_window.py`
2. Click **"Εγγραφή" (Register)** to create an account
3. Choose your role: **Student** or **Admin**
4. Log in with your credentials

> **Future Enhancement**: A standalone **installer (.exe/.msi)** will be provided in a future release, allowing you to install the application directly on your computer without needing Python or manual dependency installation.


### As a Student
1. **Browse Courses** - View available courses in the "Διαθέσιμα Μαθήματα" tab
2. **Enroll** - Click "Εγγραφή" on any course
3. **Access Lectures** - Go to "Διαλέξεις" to view PDF materials
4. **Take Quizzes** - Navigate to "Online Εξέταση" → Select course → Select quiz → Start
5. **Track Progress** - Check "Στατιστικά" for your quiz performance

### As an Admin
1. **Manage Courses** - Create/edit/delete courses with categories, dates, descriptions
2. **Upload Lectures** - Add PDF files to course lectures
3. **Create Quizzes** - Build quizzes with multiple questions
4. **View Analytics** - Monitor student performance in "Στατιστικά Quiz"

---

## Database Schema

The application uses **SQLite** with the following tables:

### `users`
| Column | Type | Constraints |
|--------|------|-------------|
| `user_id` | INTEGER | PRIMARY KEY, AUTOINCREMENT |
| `username` | TEXT | UNIQUE, NOT NULL |
| `email` | TEXT | UNIQUE, NOT NULL |
| `password` | TEXT | NOT NULL (PBKDF2 hash) |
| `role` | TEXT | NOT NULL ('student' / 'admin') |

### `courses`
| Column | Type | Constraints |
|--------|------|-------------|
| `course_id` | INTEGER | PRIMARY KEY, AUTOINCREMENT |
| `name` | TEXT | NOT NULL |
| `description` | TEXT | |
| `category` | TEXT | NOT NULL |
| `instructor` | TEXT | |
| `admin_id` | INTEGER | FOREIGN KEY → users(user_id) |
| `start_date` | TEXT | |
| `end_date` | TEXT | |

### `lectures`
| Column | Type | Constraints |
|--------|------|-------------|
| `lecture_id` | INTEGER | PRIMARY KEY, AUTOINCREMENT |
| `course_id` | INTEGER | FOREIGN KEY → courses(course_id) |
| `title` | TEXT | |
| `pdf_data` | BLOB | PDF file content |
| `pdf_filename` | TEXT | Original filename |

### `enrollments`
| Column | Type | Constraints |
|--------|------|-------------|
| `enrollment_id` | INTEGER | PRIMARY KEY, AUTOINCREMENT |
| `student_id` | INTEGER | FOREIGN KEY → users(user_id) |
| `course_id` | INTEGER | FOREIGN KEY → courses(course_id) |
| `enrollment_date` | TEXT | DEFAULT CURRENT_TIMESTAMP |

### `quizzes`
| Column | Type | Constraints |
|--------|------|-------------|
| `quiz_id` | INTEGER | PRIMARY KEY, AUTOINCREMENT |
| `course_id` | INTEGER | FOREIGN KEY → courses(course_id) |
| `title` | TEXT | NOT NULL |
| `description` | TEXT | |
| `time_limit` | INTEGER | Minutes |
| `created_by` | INTEGER | FOREIGN KEY → users(user_id) |

### `questions`
| Column | Type | Constraints |
|--------|------|-------------|
| `question_id` | INTEGER | PRIMARY KEY, AUTOINCREMENT |
| `quiz_id` | INTEGER | FOREIGN KEY → quizzes(quiz_id) |
| `question_text` | TEXT | NOT NULL |
| `question_type` | TEXT | 'multiple_choice' / 'true_false' |
| `options` | TEXT | JSON array of options |
| `correct_answer` | TEXT | |
| `points` | INTEGER | DEFAULT 1 |

### `quiz_attempts`
| Column | Type | Constraints |
|--------|------|-------------|
| `attempt_id` | INTEGER | PRIMARY KEY, AUTOINCREMENT |
| `quiz_id` | INTEGER | FOREIGN KEY → quizzes(quiz_id) |
| `student_id` | INTEGER | FOREIGN KEY → users(user_id) |
| `score` | REAL | |
| `max_score` | REAL | |
| `started_at` | TEXT | |
| `completed_at` | TEXT | |
| `answers` | TEXT | JSON |

---

## 🔑 Key Modules

### `db.py` - Database Layer
- **Connection management** with foreign key enforcement
- **Password hashing** using PBKDF2-SHA256 (600k iterations)
- **Schema migrations** for backward compatibility
- **CRUD operations** for all entities

### `main_window.py` - Application Entry
- Landing page with background image
- Login/Register card switching
- Role-based routing to dashboards

### `course_management_window.py` - Main Dashboard
- **Sidebar navigation** (collapsible with animation)
- **Stacked widget** for page switching
- **Role-aware UI** (different menus for student/admin)

### `lectures_functions/lectures_functions.py` - PDF Viewer
- **PyMuPDF** for PDF rendering to images
- **QtWebEngine** for high-quality display
- **Page navigation** (prev/next, page indicator)
- **Zoom & fit** controls

### `quiz_functions/` - Quiz System
- **QuizExecutionDialog** - Timed quiz taking interface
- **QuizSelectionDialog** - Admin course selection for quiz creation
- **StudentQuizSelectionDialog** - Student quiz browsing

### `styles_css/styles.py` - Centralized Styling
- All QSS stylesheets in one place
- Consistent color scheme (#34405e, #1a252f, #2c3e50)
- Reusable style functions for containers, buttons, lists

---

## 📲 Screenshots

> ```markdown
> ![Login Screen](screenshots/login.png)
> ![Student Dashboard](screenshots/student-dashboard.png)
> ![Admin Dashboard](screenshots/admin-dashboard.png)
> ![PDF Lecture Viewer](screenshots/pdf-viewer.png)
> ![Quiz Interface](screenshots/quiz.png)
> ```

---

## 📝 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 📩 Support

For questions or issues, please open a GitHub Issue or contact me at dfournarakos567@gmail.com 

---