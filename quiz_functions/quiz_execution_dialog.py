from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QRadioButton,
    QPushButton, QMessageBox, QButtonGroup
)
from PyQt5.QtCore import Qt
from db import save_quiz_result
import sqlite3

class QuizExecutionDialog(QDialog):
    def __init__(self, student_id, quiz_id, parent=None):
        super().__init__(parent)
        self.student_id = student_id
        self.quiz_id = quiz_id

        self.setWindowTitle("Εκτέλεση Quiz")
        self.setGeometry(100, 100, 600, 400)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.questions = self.load_questions()
        if not self.questions:
            QMessageBox.warning(self, "Σφάλμα", "Δεν βρέθηκαν ερωτήσεις για αυτό το quiz.")
            self.reject()
            return

        self.current_index = 0
        self.user_answers = {}  # Αποθήκευση απαντήσεων

        self.title = QLabel()
        self.layout.addWidget(self.title)

        self.question_label = QLabel()
        self.layout.addWidget(self.question_label)

        self.options_group = QButtonGroup(self)
        self.option_a = QRadioButton()
        self.option_b = QRadioButton()
        self.option_c = QRadioButton()
        self.option_d = QRadioButton()

        for btn in [self.option_a, self.option_b, self.option_c, self.option_d]:
            self.layout.addWidget(btn)
            self.options_group.addButton(btn)

        self.submit_btn = QPushButton("Υποβολή Απάντησης")
        self.submit_btn.clicked.connect(self.submit_answer)  # Με μήνυμα
        self.layout.addWidget(self.submit_btn)

        self.nav_layout = QHBoxLayout()

        self.prev_btn = QPushButton("← Προηγούμενη Ερώτηση")
        self.prev_btn.clicked.connect(self.previous_question)
        self.prev_btn.setEnabled(False)
        self.nav_layout.addWidget(self.prev_btn, alignment=Qt.AlignLeft)

        self.final_btn = QPushButton("Τελική Υποβολή")
        self.final_btn.clicked.connect(self.finish_quiz)
        self.final_btn.setVisible(False)

        self.next_btn = QPushButton("Επόμενη Ερώτηση →")
        self.next_btn.clicked.connect(self.next_question)  # Χωρίς μήνυμα
        self.nav_layout.addWidget(self.next_btn, alignment=Qt.AlignRight)

        self.layout.addLayout(self.nav_layout)

        self.show_question()

    def load_questions(self):
        conn = sqlite3.connect("lms.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT question_text, option_a, option_b, option_c, option_d, correct_option
            FROM questions
            WHERE quiz_id = ?
        """, (self.quiz_id,))
        results = cursor.fetchall()
        conn.close()
        return results

    def show_question(self):
        q = self.questions[self.current_index]
        self.title.setText(f"Ερώτηση {self.current_index + 1} από {len(self.questions)}")
        self.question_label.setText(q[0])
        self.option_a.setText(f"A. {q[1]}")
        self.option_b.setText(f"B. {q[2]}")
        self.option_c.setText(f"C. {q[3]}")
        self.option_d.setText(f"D. {q[4]}")

        self.options_group.setExclusive(False)
        for btn in self.options_group.buttons():
            btn.setChecked(False)
        self.options_group.setExclusive(True)

        # Αν είχε απαντηθεί ήδη
        if self.current_index in self.user_answers:
            selected = self.user_answers[self.current_index]
            idx = ord(selected) - 65  # A->0, B->1...
            if 0 <= idx <= 3:
                self.options_group.buttons()[idx].setChecked(True)

        self.prev_btn.setEnabled(self.current_index > 0)

        if self.current_index == len(self.questions) - 1:
            self.next_btn.setVisible(False)
            self.final_btn.setVisible(True)
            if self.nav_layout.indexOf(self.final_btn) == -1:
                self.nav_layout.addWidget(self.final_btn, alignment=Qt.AlignRight)
        else:
            self.next_btn.setVisible(True)
            self.final_btn.setVisible(False)

    def save_answer(self):
        selected = None
        for btn in self.options_group.buttons():
            if btn.isChecked():
                selected = btn.text()[0]  # Παίρνουμε το γράμμα π.χ. 'A'
                break

        if not selected:
            QMessageBox.warning(self, "Προσοχή", "Επέλεξε μία απάντηση.")
            return False

        # Αποθήκευση απάντησης
        self.user_answers[self.current_index] = selected
        return True

    def submit_answer(self):
        if not self.save_answer():
            return
        # Μήνυμα επιβεβαίωσης μόνο εδώ
        QMessageBox.information(
            self,
            "Απάντηση Υποβλήθηκε",
            f"✅ Υποβάλατε την απάντηση: {self.user_answers[self.current_index]}"
        )

    def next_question(self):
        if not self.save_answer():
            return
        if self.current_index < len(self.questions) - 1:
            self.current_index += 1
            self.show_question()

    def previous_question(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.show_question()

    def finish_quiz(self):
        if not self.save_answer():
            return

        correct_count = 0
        for idx, user_ans in self.user_answers.items():
            correct = self.questions[idx][5].upper()
            if user_ans == correct:
                correct_count += 1

        total = len(self.questions)
        score = round((correct_count / total) * 100, 2)
        save_quiz_result(self.student_id, self.quiz_id, score)
        QMessageBox.information(self, "Ολοκλήρωση", f"Τέλος quiz.\nΣκορ: {score}%")
        self.accept()
