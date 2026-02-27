import sqlite3
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QMessageBox, QButtonGroup
)

class TakeQuizWidget(QWidget):
    def __init__(self, quiz_id, student_id=None, parent=None):
        super().__init__(parent)
        self.quiz_id = quiz_id
        self.student_id = student_id
        self.setWindowTitle("Εξέταση Quiz")

        self.layout = QVBoxLayout(self)

        self.question_label = QLabel("Ερώτηση:")
        self.layout.addWidget(self.question_label)

        self.options = []
        self.button_group = QButtonGroup(self)
        for i in range(4):
            btn = QPushButton()
            btn.setCheckable(True)
            self.layout.addWidget(btn)
            self.options.append(btn)
            self.button_group.addButton(btn, i)

        self.submit_btn = QPushButton("Υποβολή Απάντησης")
        self.submit_btn.clicked.connect(self.submit_answer)
        self.layout.addWidget(self.submit_btn)

        self.prev_btn = QPushButton("Προηγούμενη Ερώτηση")
        self.prev_btn.clicked.connect(self.previous_question)
        self.layout.addWidget(self.prev_btn)

        self.next_btn = QPushButton("Επόμενη Ερώτηση")
        self.next_btn.clicked.connect(self.next_question)
        self.layout.addWidget(self.next_btn)

        self.final_submit_btn = QPushButton("Τελική Υποβολή")
        self.final_submit_btn.clicked.connect(self.final_submit)
        self.layout.addWidget(self.final_submit_btn)

        self.questions = []
        self.current_index = 0
        self.user_answers = {}

        self.load_all_questions()
        self.update_ui()

    def load_all_questions(self):
        conn = sqlite3.connect('lms.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT question_id, question_text, option_a, option_b, option_c, option_d, correct_option
            FROM questions
            WHERE quiz_id = ?
            ORDER BY question_id
            LIMIT 5
        """, (self.quiz_id,))
        self.questions = cursor.fetchall()
        conn.close()

    def update_ui(self):
        if not self.questions:
            QMessageBox.information(self, "Ολοκλήρωση", "Δεν υπάρχουν ερωτήσεις για αυτό το quiz.")
            self.setDisabled(True)
            return

        q = self.questions[self.current_index]
        self.question_label.setText(f"Ερώτηση {self.current_index+1}: {q[1]}")

        options_text = q[2:6]
        for i, btn in enumerate(self.options):
            btn.setText(options_text[i])
            btn.setChecked(False)

        if self.current_index in self.user_answers:
            answer = self.user_answers[self.current_index]
            idx = ord(answer) - 65
            if 0 <= idx < len(self.options):
                self.options[idx].setChecked(True)

        self.prev_btn.setVisible(self.current_index > 0)
        self.next_btn.setVisible(self.current_index < len(self.questions) - 1)
        self.final_submit_btn.setVisible(self.current_index == len(self.questions) - 1)

    def submit_answer(self):
        selected_btn = None
        for btn in self.options:
            if btn.isChecked():
                selected_btn = btn
                break

        if not selected_btn:
            QMessageBox.warning(self, "Προειδοποίηση", "Επίλεξε μια απάντηση.")
            return

        selected_idx = self.options.index(selected_btn)
        selected_letter = chr(65 + selected_idx)

        self.user_answers[self.current_index] = selected_letter

        correct_option = self.questions[self.current_index][6]
        if selected_letter == correct_option:
            QMessageBox.information(self, "Σωστό", "Σωστή απάντηση!")
        else:
            QMessageBox.information(self, "Λάθος", f"Λάθος. Η σωστή απάντηση είναι: {correct_option}")

    def next_question(self):
        if self.current_index < len(self.questions) - 1:
            self.current_index += 1
            self.update_ui()

    def previous_question(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.update_ui()

    def final_submit(self):
        score = 0
        for idx, user_ans in self.user_answers.items():
            correct_ans = self.questions[idx][6]
            if user_ans == correct_ans:
                score += 1

        QMessageBox.information(self, "Τελική Υποβολή", f"Η βαθμολογία σου: {score} / {len(self.questions)}")
        self.setDisabled(True)  
