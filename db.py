import base64
import hashlib
import hmac
import secrets
import sqlite3
import os
from datetime import datetime

PASSWORD_HASH_ALGORITHM = "pbkdf2_sha256"
PASSWORD_HASH_ITERATIONS = 600_000

def hash_password(password):
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PASSWORD_HASH_ITERATIONS,
    )
    salt_text = base64.b64encode(salt).decode("ascii")
    digest_text = base64.b64encode(digest).decode("ascii")
    return f"{PASSWORD_HASH_ALGORITHM}${PASSWORD_HASH_ITERATIONS}${salt_text}${digest_text}"

def verify_password(password, stored_value):
    if stored_value.startswith(f"{PASSWORD_HASH_ALGORITHM}$"):
        try:
            algorithm, iterations_text, salt_text, digest_text = stored_value.split("$")
            if algorithm != PASSWORD_HASH_ALGORITHM:
                return False, False

            iterations = int(iterations_text)
            salt = base64.b64decode(salt_text, validate=True)
            expected = base64.b64decode(digest_text, validate=True)
            actual = hashlib.pbkdf2_hmac(
                "sha256", password.encode("utf-8"), salt, iterations
            )
            return hmac.compare_digest(actual, expected), False
        except (ValueError, TypeError):
            return False, False

    # Existing users are migrated after a successful legacy plaintext login.
    try:
        valid = hmac.compare_digest(
            password.encode("utf-8"), stored_value.encode("utf-8")
        )
    except (AttributeError, UnicodeEncodeError):
        return False, False
    return valid, valid

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
            FOREIGN KEY (admin_id) REFERENCES users(user_id)
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

    # Έλεγχος και προσθήκη στηλών για αποθήκευση PDF απευθείας στη βάση -Schema Migration για τον πίνακα lectures- Αναβαθμίζει αυτόματα το schema χωρίς να χρειάζεται να ξαναφτιάξεις τη βάση από την αρχή
    cursor.execute("PRAGMA table_info(lectures)") #Ρωτά τη SQLite ποιες στήλες έχει ήδη ο πίνακας lectures.
    lecture_columns = [info[1] for info in cursor.fetchall()]#Παίρνει τα αποτελέσματα και κρατά μόνο τα ονόματα των στηλών
    if 'file_name' not in lecture_columns: #Αν δεν υπάρχει η στήλη file_name, τη δημιουργεί
        cursor.execute("ALTER TABLE lectures ADD COLUMN file_name TEXT")
    if 'mime_type' not in lecture_columns: #Αν δεν υπάρχει η mime_type, τη δημιουργεί με default τιμή 'application/pdf',που είναι ο τύπος αρχείου(pdf)
        cursor.execute("ALTER TABLE lectures ADD COLUMN mime_type TEXT DEFAULT 'application/pdf'")
    if 'pdf_data' not in lecture_columns: #Αν δεν υπάρχει η pdf_data, τη δημιουργεί ως BLOB(bytes του PDF)
        cursor.execute("ALTER TABLE lectures ADD COLUMN pdf_data BLOB")

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

    conn.commit()
    conn.close()

def initialize_database():
    create_tables()

def require_admin(cursor, actor_user_id):
    cursor.execute(
        "SELECT 1 FROM users WHERE user_id = ? AND role = 'admin'",
        (actor_user_id,),
    )
    if cursor.fetchone() is None:
        raise PermissionError("Απαιτούνται δικαιώματα διαχειριστή.")

def require_student(cursor, actor_user_id):
    cursor.execute(
        "SELECT 1 FROM users WHERE user_id = ? AND role = 'student'",
        (actor_user_id,),
    )
    if cursor.fetchone() is None:
        raise PermissionError("Απαιτούνται δικαιώματα φοιτητή.")

def add_lecture_to_course(actor_user_id, course_id, file_name, pdf_data, mime_type="application/pdf"): #mime_type για να ξέρω τι είδους αρχείο είναι,σε αυτή την περίπτωση pdf,αλλά μπορεί να επεκταθεί και σε άλλους τύπους αρχείων στο μέλλον
    """Αποθηκεύει PDF διάλεξης ως Binary Large Object-BLOB(σαν raw δυαδικά δεδομένα(raw bytes-PDF) μέσα σε στήλη της βάσης)"""
    #Παίρνω το PDF ως bytes,Τα bytes μπαίνουν στη στήλη pdf_data του πίνακα lectures,
    #Όταν θέλω να το ανοίξω, διαβάζω τη στήλη και παίρνω πάλι bytes.Αυτά τα bytes τα δίνω στον viewer (fitz) για render.
    conn = connect_db()
    try:
        cursor = conn.cursor()
        require_admin(cursor, actor_user_id)
        title = os.path.splitext(file_name)[0] #χωρίζει το όνομα αρχείου σε δύο μέρη,το όνομα και την καταληξη,εγω παίρνω μόνο το όνομα [0]
        cursor.execute("""
            INSERT INTO lectures (course_id, title, file_name, mime_type, pdf_data)
            VALUES (?, ?, ?, ?, ?)
        """, (course_id, title, file_name, mime_type, pdf_data))
        conn.commit()
    finally:
        conn.close()

def get_lectures_by_course(course_id):
    """Επιστρέφει lecture_id και όνομα αρχείου για το μάθημα."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT lecture_id, COALESCE(file_name, title, 'lecture.pdf')
        FROM lectures
        WHERE course_id = ?
        ORDER BY lecture_id DESC
    """, (course_id,))
    #SELECT lecture_id, COALESCE(file_name, title, 'lecture.pdf') = Επιστρέφει το lecture_id και Coalesce το όνομα αρχείου,COALESCE(a, b, c) σημαίνει: πάρε την πρώτη τιμή που δεν είναι NULL
    #Παίρνει το  file_name αν υπάρχει,αν όχι παίρνει το title,αν και αυτό είναι NULL τότε επιστρέφει 'lecture.pdf' ως default όνομα αρχείου.Έτσι εξασφαλίζουμε ότι πάντα θα έχουμε ένα όνομα αρχείου για κάθε διάλεξη,ακόμα και αν δεν έχει ανέβει PDF ή δεν έχει οριστεί τίτλος.
    #Order by lecture_id DESC για να εμφανίζονται οι πιο πρόσφατες διαλέξεις πρώτες στη λίστα.(Ταξινομεί από το μεγαλύτερο id στο μικρότερο.)
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_lecture_pdf_by_id(lecture_id):
    """Επιστρέφει τα bytes του PDF για συγκεκριμένη διάλεξη."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT pdf_data FROM lectures WHERE lecture_id = ?", (lecture_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

#  Συναρτήσεις για εγγραφές 
def create_course(actor_user_id, name, description, category, instructor, start_date, end_date):
    conn = connect_db()
    try:
        cursor = conn.cursor()
        require_admin(cursor, actor_user_id)
        cursor.execute('''
            INSERT INTO courses (name, description, category, instructor, start_date, end_date, admin_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, description, category, instructor, start_date, end_date, actor_user_id))
        conn.commit()
    finally:
        conn.close()

def update_course(actor_user_id, course_id, name, description, category, instructor, start_date, end_date):
    conn = connect_db()
    try:
        cursor = conn.cursor()
        require_admin(cursor, actor_user_id)
        cursor.execute('''
            UPDATE courses
            SET name = ?, description = ?, category = ?, instructor = ?, start_date = ?, end_date = ?
            WHERE course_id = ?
        ''', (name, description, category, instructor, start_date, end_date, course_id))
        conn.commit()
    finally:
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

def unenroll_user_from_course(user_id, course_id):
    """Κάνει Απεγγραφή έναν φοιτητή από ενα μάθημα"""
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM enrollments WHERE user_id = ? AND course_id = ?", (user_id,course_id))
        conn.commit()
        return True   
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def create_quiz_in_db(actor_user_id, title, description, course_id):
    conn = connect_db()
    try:
        cursor = conn.cursor()
        require_admin(cursor, actor_user_id)
        cursor.execute("""
            INSERT INTO quizzes (course_id, title, description)
            VALUES (?, ?, ?)
        """, (course_id, title, description))
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()

def get_quizzes_by_course(course_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT quiz_id, title FROM quizzes WHERE course_id = ?
    """, (course_id,))
    rows = cursor.fetchall()
    
    conn.close()
    return [{'quiz_id': row[0], 'title': row[1]} for row in rows]


def add_question_to_quiz(actor_user_id, quiz_id, question_text, option_a, option_b, option_c, option_d, correct_option):
    print(f"DEBUG: Κλήση add_question_to_quiz με quiz_id: {quiz_id}, question_text: '{question_text}', correct_option: {correct_option}")
    conn = connect_db()
    cursor = conn.cursor()
    try:
        require_admin(cursor, actor_user_id)
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

def get_questions_by_quiz_id(quiz_id):
    """Φορτώνει όλες τις ερωτήσεις για ένα συγκεκριμένο quiz"""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT question_text, option_a, option_b, option_c, option_d, correct_option
        FROM questions
        WHERE quiz_id = ?
        ORDER BY question_id
    """, (quiz_id,))
    results = cursor.fetchall()
    conn.close()
    return results

def get_all_courses():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM courses ORDER BY name')
    courses = cursor.fetchall()
    conn.close()
    return courses

def delete_course(actor_user_id, course_id):
    conn = connect_db()
    try:
        cursor = conn.cursor()
        require_admin(cursor, actor_user_id)
        cursor.execute('DELETE FROM courses WHERE course_id = ?', (course_id,))
        conn.commit()
    finally:
        conn.close()

def get_user_by_id(user_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT user_id, username, email, role FROM users WHERE user_id = ?",
        (user_id,)
    )
    row = cursor.fetchone()
    conn.close()
    return row

def get_user_for_login(email, password):
    conn = connect_db()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT user_id, username, password, role FROM users WHERE email = ?",
            (email,),
        )
        user = cursor.fetchone()
        if user is None:
            return None

        valid, legacy_password = verify_password(password, user[2])
        if not valid:
            return None

        if legacy_password:
            cursor.execute(
                "UPDATE users SET password = ? WHERE user_id = ?",
                (hash_password(password), user[0]),
            )
            conn.commit()

        return user[0], user[1], user[3]
    finally:
        conn.close()

def user_exists_by_email(email):
    conn = connect_db()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM users WHERE email = ?", (email,))
        return cursor.fetchone() is not None
    finally:
        conn.close()

def user_exists_by_username(username):
    conn = connect_db()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
        return cursor.fetchone() is not None
    finally:
        conn.close()

def create_user(username, email, password, role):
    conn = connect_db()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)",
            (username, email, hash_password(password), role),
        )
        conn.commit()
    finally:
        conn.close()


#Συνάρτηση για αποθήκευση βαθμολογίας
def save_quiz_result(actor_user_id, quiz_id, score):
    """Αποθηκεύει αποτέλεσμα μόνο για εγγεγραμμένο student actor."""
    conn = connect_db()
    try:
        cursor = conn.cursor()
        if not 0 <= score <= 100:
            raise ValueError("Η βαθμολογία πρέπει να είναι μεταξύ 0 και 100.")

        cursor.execute(
            """
            SELECT 1
            FROM users u
            JOIN enrollments e ON e.user_id = u.user_id
            JOIN quizzes q ON q.course_id = e.course_id
            WHERE u.user_id = ? AND u.role = 'student' AND q.quiz_id = ?
            """,
            (actor_user_id, quiz_id),
        )
        if cursor.fetchone() is None:
            raise PermissionError("Ο χρήστης δεν έχει δικαίωμα υποβολής σε αυτό το quiz.")

        cursor.execute("""
            INSERT INTO quiz_results (student_id, quiz_id, score, date_taken)
            VALUES (?, ?, ?, ?)
        """, (actor_user_id, quiz_id, score, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
    finally:
        conn.close()

#Συνάρτηση για στατιστικά quiz(admin)
def get_statistics_for_quiz(actor_user_id, quiz_id):
    """Επιστρέφει στατιστικά για quiz: μέσος όρος, ελάχιστο, μέγιστο και πλήθος προσπαθειών."""
    conn = connect_db()
    try:
        cursor = conn.cursor()
        require_admin(cursor, actor_user_id)
        cursor.execute("""
            SELECT AVG(score), MIN(score), MAX(score), COUNT(*)
            FROM quiz_results
            WHERE quiz_id = ?
        """, (quiz_id,))
        result = cursor.fetchone()
    finally:
        conn.close()
    return {
        "average": result[0] or 0.0,
        "min": result[1] or 0.0,
        "max": result[2] or 0.0,
        "count": result[3]
    }

def get_student_scores_by_course(actor_user_id, course_id):
    conn = connect_db()
    try:
        cursor = conn.cursor()
        require_student(cursor, actor_user_id)
        cursor.execute("""
            SELECT q.title, r.score
            FROM quiz_results r
            JOIN quizzes q ON r.quiz_id = q.quiz_id
            WHERE r.student_id = ? AND q.course_id = ?
        """, (actor_user_id, course_id))
        rows = cursor.fetchall()
    finally:
        conn.close()
    return [{'title': row[0], 'score': row[1]} for row in rows]

def get_courses_with_stats(actor_user_id):
    conn = connect_db()
    try:
        cursor = conn.cursor()
        require_student(cursor, actor_user_id)
        query = """
                SELECT DISTINCT c.course_id, c.name
                FROM courses c
                JOIN quizzes q ON c.course_id = q.course_id
                JOIN quiz_results r ON q.quiz_id = r.quiz_id
                WHERE r.student_id = ?
                """
        cursor.execute(query, (actor_user_id,))
        courses = cursor.fetchall()
    finally:
        conn.close()
    return courses


def get_student_quiz_leaderboard(actor_user_id):
    """Επιστρέφει όλες τις προσπάθειες quiz του student με μάθημα, quiz, ημερομηνία και βαθμό."""
    conn = connect_db()
    try:
        cursor = conn.cursor()
        require_student(cursor, actor_user_id)
        cursor.execute(
            """
            SELECT c.name, q.title, r.date_taken, r.score
            FROM quiz_results r
            JOIN quizzes q ON q.quiz_id = r.quiz_id
            JOIN courses c ON c.course_id = q.course_id
            WHERE r.student_id = ?
            ORDER BY r.score DESC, r.date_taken DESC
            """,
            (actor_user_id,),
        )
        rows = cursor.fetchall()
    finally:
        conn.close()
    return rows