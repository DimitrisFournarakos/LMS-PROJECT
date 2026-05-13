"""
Διάλογοι για δημιουργία και διαχείριση Quiz.
Περιέχει τα QuizDialog και AddMultipleQuestionsDialog.
"""

import sqlite3
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox


class QuizDialog(QDialog):
    """Διάλογος για δημιουργία νέου Quiz"""
    
    def __init__(self, course_id, parent=None):
        super().__init__(parent)
        self.course_id = course_id
        self.created_quiz_id = None
        self.setWindowTitle("Δημιουργία Quiz")
        self.setGeometry(100, 100, 400, 300)
        self.layout = QVBoxLayout()

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Τίτλος Quiz")
        self.layout.addWidget(self.title_input)

        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Περιγραφή Quiz")
        self.layout.addWidget(self.description_input)

        self.create_btn = QPushButton("➕ Προσθήκη Ερωτήσεων")
        self.create_btn.clicked.connect(self.create_quiz_and_add_questions)
        self.layout.addWidget(self.create_btn)
        self.setLayout(self.layout)

    def create_quiz_and_add_questions(self):
        """Δημιουργεί ένα νέο Quiz στη βάση δεδομένων"""
        title = self.title_input.text().strip()
        desc = self.description_input.text().strip()
        
        if not title or not desc:
            QMessageBox.warning(self, "Προειδοποίηση", "Συμπλήρωσε τα πεδία.")
            return
        
        try:
            conn = sqlite3.connect("lms.db")
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO quizzes (course_id, title, description) VALUES (?, ?, ?)", 
                (self.course_id, title, desc)
            )
            conn.commit()
            self.created_quiz_id = cursor.lastrowid
            conn.close()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Σφάλμα", str(e))


class AddMultipleQuestionsDialog(QDialog):
    """Διάλογος για προσθήκη ερωτήσεων σε Quiz"""
    
    def __init__(self, quiz_id, total_questions=5, parent=None):
        super().__init__(parent)
        self.quiz_id = quiz_id
        self.total_questions = total_questions
        self.current_question = 1

        self.setWindowTitle("Προσθήκη Ερωτήσεων")
        self.setGeometry(100, 100, 400, 450)
        self.layout = QVBoxLayout()

        self.title = QLabel(
            f"Ερώτηση {self.current_question} από {self.total_questions}")
        self.layout.addWidget(self.title)

        self.question_input = QLineEdit()
        self.question_input.setPlaceholderText("Ερώτηση")
        self.layout.addWidget(self.question_input)

        self.option_a = QLineEdit()
        self.option_a.setPlaceholderText("Επιλογή A")
        self.option_b = QLineEdit()
        self.option_b.setPlaceholderText("Επιλογή B")
        self.option_c = QLineEdit()
        self.option_c.setPlaceholderText("Επιλογή C")
        self.option_d = QLineEdit()
        self.option_d.setPlaceholderText("Επιλογή D")
        self.correct_option = QLineEdit()
        self.correct_option.setPlaceholderText("Σωστή (A, B, C, D)")

        for w in [self.option_a, self.option_b, self.option_c, self.option_d, self.correct_option]:
            self.layout.addWidget(w)

        self.submit_btn = QPushButton("Υποβολή Ερώτησης")
        self.submit_btn.clicked.connect(self.submit_question)
        self.layout.addWidget(self.submit_btn)
        self.setLayout(self.layout)

    def submit_question(self):
        """Προσθέτει μια ερώτηση στο Quiz"""
        from db import add_question_to_quiz
        
        q = self.question_input.text().strip()
        ans = [self.option_a.text(), self.option_b.text(),
               self.option_c.text(), self.option_d.text()]
        correct = self.correct_option.text().strip().upper()

        if not q or not all(ans) or correct not in ['A', 'B', 'C', 'D']:
            QMessageBox.warning(self, "Σφάλμα", "Συμπληρώστε σωστά τα πεδία.")
            return

        success = add_question_to_quiz(self.quiz_id, q, *ans, correct)
        if success:
            if self.current_question < self.total_questions:
                self.current_question += 1
                self.title.setText(
                    f"Ερώτηση {self.current_question} από {self.total_questions}")
                for w in [self.question_input, self.option_a, self.option_b, self.option_c, self.option_d, self.correct_option]:
                    w.clear()
            else:
                QMessageBox.information(
                    self, "Τέλος", "Όλες οι ερωτήσεις προστέθηκαν.")
                self.accept()
