import sqlite3,os
from datetime import datetime

def connect_db():
    return sqlite3.connect("lms.db")

def create_tables():
    conn = connect_db()
    cursor = conn.cursor()

    # Πίνακας χρηστών users
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)

    # Πίνακας μαθημάτων courses
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            course_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            category TEXT NOT NULL,
            instructor TEXT,
            admin_id INTEGER,
            start_date TEXT,
            end_date TEXT,
            pdf_path TEXT,
            FOREIGN KEY (admin_id) REFERENCES users(user_id)
        )
    """)

    # Πίνακας βαθμών grades
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS grades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            course TEXT NOT NULL,
            grade REAL
        )
    """)

    # Πίνακας διαλέξεων lectures
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lectures (
            lecture_id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER,
            title TEXT,
            FOREIGN KEY(course_id) REFERENCES courses(course_id)
        )
    """)

    # Πίνακας εγγραφών φοιτητών enrollments,όταν πάει να κάνει εγγραφή σε κάποιο μαθημα από την λίστα
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS enrollments (
            enrollment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            course_id INTEGER NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(user_id),
            FOREIGN KEY(course_id) REFERENCES courses(course_id),
            UNIQUE(user_id, course_id)
        )
    """)

    # Πίνακας Quiz,λίστα με τα υπάρχοντα quiz για κάθε μαθημα
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS quizzes (
        quiz_id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        FOREIGN KEY(course_id) REFERENCES courses(course_id)
    )
""")# Έλεγχος και προσθήκη της στήλης description αν δεν υπάρχει
    cursor.execute("PRAGMA table_info(quizzes)")
    columns = [info[1] for info in cursor.fetchall()]
    if 'description' not in columns:
        cursor.execute("ALTER TABLE quizzes ADD COLUMN description TEXT")

    # Πίνακας Ερωτήσεων Quiz
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            question_id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_id INTEGER NOT NULL,
            question_text TEXT NOT NULL,
            option_a TEXT NOT NULL,
            option_b TEXT NOT NULL,
            option_c TEXT NOT NULL,
            option_d TEXT NOT NULL,
            correct_option TEXT NOT NULL,
            FOREIGN KEY(quiz_id) REFERENCES quizzes(quiz_id)
        )
    """)

    # Πίνακας προσπαθειών φοιτητών για quiz
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quiz_attempts (
            attempt_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            quiz_id INTEGER NOT NULL,
            score REAL,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(user_id),
            FOREIGN KEY(quiz_id) REFERENCES quizzes(quiz_id)
        )
    """)
        # Πίνακας αποτελεσμάτων quiz
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quiz_results (
            result_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            quiz_id INTEGER NOT NULL,
            score REAL NOT NULL,
            date_taken TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (student_id) REFERENCES users(user_id),
            FOREIGN KEY (quiz_id) REFERENCES quizzes(quiz_id)
        )
    """)


    # Προσθήκη της στήλης pdf_path αν λείπει
    cursor.execute("PRAGMA table_info(courses)")
    columns = [info[1] for info in cursor.fetchall()]
    if 'pdf_path' not in columns:
        cursor.execute("ALTER TABLE courses ADD COLUMN pdf_path TEXT")

    conn.commit()
    conn.close()

def initialize_database():
    create_tables()
    if not os.path.exists("lectures"):
        os.makedirs("lectures")

#  Συναρτήσεις για εγγραφές 
def create_course(name, description, category, instructor, start_date, end_date):
    conn = sqlite3.connect('lms.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO courses (name, description, category, instructor, start_date, end_date)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, description, category, instructor, start_date, end_date))
    conn.commit()
    conn.close()

def update_course(course_id, name, description, category, instructor, start_date, end_date):
    conn = sqlite3.connect('lms.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE courses
        SET name = ?, description = ?, category = ?, instructor = ?, start_date = ?, end_date = ?
        WHERE course_id = ?
    ''', (name, description, category, instructor, start_date, end_date, course_id))
    conn.commit()
    conn.close()

def get_enrolled_courses(user_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.* FROM courses c
        JOIN enrollments e ON c.course_id = e.course_id
        WHERE e.user_id = ?
    """, (user_id,))
    courses = cursor.fetchall()
    conn.close()
    return courses

def get_available_courses_for_user(user_id):
    """Επιστρέφει τα μαθήματα στα οποία ΔΕΝ είναι εγγεγραμμένος ο φοιτητής"""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM courses
        WHERE course_id NOT IN (
            SELECT course_id FROM enrollments WHERE user_id = ?
        )
    """, (user_id,))
    results = cursor.fetchall()
    conn.close()
    return results

def enroll_user_in_course(user_id, course_id):
    """Εγγράφει έναν φοιτητή σε μάθημα (αν δεν είναι ήδη εγγεγραμμένος)"""
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)", (user_id, course_id))
        conn.commit()
    except sqlite3.IntegrityError:
        pass  # Ήδη εγγεγραμμένος
    conn.close()

def create_quiz_in_db(title, description, course_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO quizzes (course_id, title, description)
        VALUES (?, ?, ?)
    """, (course_id, title, description))
    conn.commit()
    conn.close()

def get_quizzes_by_course(course_id):
    conn = sqlite3.connect("lms.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT quiz_id, title FROM quizzes WHERE course_id = ?
    """, (course_id,))
    rows = cursor.fetchall()
    print(f"DEBUG: Quizzes for course {course_id}: {rows}")
    conn.close()
    return [{'quiz_id': row[0], 'title': row[1]} for row in rows]


def delete_quiz_by_id(quiz_id):
    conn = sqlite3.connect("lms.db")
    cursor = conn.cursor()
    # Διαγραφή ερωτήσεων που ανήκουν στο quiz
    cursor.execute("DELETE FROM questions WHERE quiz_id = ?", (quiz_id,))
    # Διαγραφή quiz
    cursor.execute("DELETE FROM quizzes WHERE quiz_id = ?", (quiz_id,))
    conn.commit()
    conn.close()

def add_question_to_quiz(quiz_id, question_text, option_a, option_b, option_c, option_d, correct_option):
    print(f"DEBUG: Κλήση add_question_to_quiz με quiz_id: {quiz_id}, question_text: '{question_text}', correct_option: {correct_option}")
    conn = sqlite3.connect('lms.db')
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO questions (quiz_id, question_text, option_a, option_b, option_c, option_d, correct_option)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (quiz_id, question_text, option_a, option_b, option_c, option_d, correct_option))
        conn.commit()
        print(f"DEBUG: Ερώτηση προστέθηκε επιτυχώς στο quiz_id: {quiz_id}")
        conn.close()
        return True
    except Exception as e:
        print(f"DEBUG: Σφάλμα κατά την προσθήκη ερώτησης: {e}")
        conn.rollback()
        conn.close()
        return False

def get_all_courses():
    conn = sqlite3.connect('lms.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM courses')
    courses = cursor.fetchall()
    conn.close()
    return courses

def delete_course(course_id):
    conn = sqlite3.connect('lms.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM courses WHERE course_id = ?', (course_id,))
    conn.commit()
    conn.close()


#Συνάρτηση για αποθήκευση βαθμολογίας
def save_quiz_result(student_id, quiz_id, score):
    """Αποθηκεύει τη βαθμολογία του φοιτητή για συγκεκριμένο quiz."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO quiz_results (student_id, quiz_id, score, date_taken)
        VALUES (?, ?, ?, ?)
    """, (student_id, quiz_id, score, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

#Συνάρτηση για στατιστικά quiz(admin)
def get_statistics_for_quiz(quiz_id):
    """Επιστρέφει στατιστικά για quiz: μέσος όρος, ελάχιστο, μέγιστο και πλήθος προσπαθειών."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT AVG(score), MIN(score), MAX(score), COUNT(*)
        FROM quiz_results
        WHERE quiz_id = ?
    """, (quiz_id,))
    result = cursor.fetchone()
    conn.close()
    return {
        "average": result[0] or 0.0,
        "min": result[1] or 0.0,
        "max": result[2] or 0.0,
        "count": result[3]
    }

def get_student_scores_by_course(student_id, course_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT q.title, r.score
        FROM quiz_results r
        JOIN quizzes q ON r.quiz_id = q.quiz_id
        WHERE r.student_id = ? AND q.course_id = ?
    """, (student_id, course_id))
    rows = cursor.fetchall()
    conn.close()
    return [{'title': row[0], 'score': row[1]} for row in rows]

def get_courses_with_stats(student_id):
    conn = connect_db()
    cursor = conn.cursor()
    # Φέρνουμε μαθήματα που έχουν τουλάχιστον μία εγγραφή στον πίνακα scores για τον συγκεκριμένο μαθητή
    #ΕΞΤΡΑ ΠΑΡΑΜΕΤΡΟΣ,ΝΑ ΕΧΕΙ ΚΑΝΕΙ ΤΟΥΛΑΧΙΣΤΟΝ ΕΝΑ QUIZ
    #Φερνω πίσω τον student που πλήρεί αυτή την προυπόθεση
    query = """
            SELECT DISTINCT c.course_id, c.name
            FROM courses c
            JOIN quizzes q ON c.course_id = q.course_id
            JOIN quiz_results r ON q.quiz_id = r.quiz_id 
            WHERE r.student_id = ?      
            """
    cursor.execute(query,(student_id,))
    courses = cursor.fetchall()
    conn.close()
    return courses