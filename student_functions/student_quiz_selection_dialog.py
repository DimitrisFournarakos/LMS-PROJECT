from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QListWidget, QPushButton, QMessageBox
)
from db import get_enrolled_courses, get_quizzes_by_course
from quiz_functions.quiz_execution_dialog import QuizExecutionDialog


class StudentQuizSelectionDialog(QDialog):
    def __init__(self, student_id, parent=None):
        super().__init__(parent)
        self.student_id = student_id
        self.setWindowTitle("Επιλογή Μαθήματος και Quiz")
        self.setGeometry(300, 200, 500, 400)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.label = QLabel("Επιλέξτε Μάθημα και Quiz")
        self.layout.addWidget(self.label)

        self.course_list = QListWidget()
        self.course_list.itemClicked.connect(self.load_quizzes)
        self.layout.addWidget(self.course_list)

        self.quiz_list = QListWidget()
        self.layout.addWidget(self.quiz_list)

        self.start_btn = QPushButton("Έναρξη Quiz")
        self.start_btn.clicked.connect(self.start_selected_quiz)
        self.layout.addWidget(self.start_btn)

        self.load_courses()

    def load_courses(self):
        courses = get_enrolled_courses(self.student_id)
        self.course_list.clear()
        for course in courses:
            self.course_list.addItem(f"{course[0]} - {course[1]}")

    def load_quizzes(self, item):
        course_id = int(item.text().split(" - ")[0])
        quizzes = get_quizzes_by_course(course_id)
        self.quiz_list.clear()
        for quiz in quizzes:
            self.quiz_list.addItem(f"{quiz['quiz_id']} - {quiz['title']}")

    def start_selected_quiz(self):
        selected = self.quiz_list.currentItem()
        if not selected:
            QMessageBox.warning(self, "Προειδοποίηση", "Παρακαλώ επιλέξτε ένα quiz.")
            return
        quiz_id = int(selected.text().split(" - ")[0])

        # Άνοιγμα παραθύρου Quiz
        widget = QuizExecutionDialog(student_id=self.student_id, quiz_id=quiz_id)
        widget.exec_()  
