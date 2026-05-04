from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QPushButton, QMessageBox
)
from PyQt5.QtCore import Qt
from db import get_enrolled_courses, get_quizzes_by_course
from quiz_functions.quiz_execution_dialog import QuizExecutionDialog
from styles_css.styles import window_title_frame_style


class StudentQuizSelectionDialog(QWidget):
    def __init__(self, student_id, parent_window=None):
        super().__init__(parent_window)
        self.student_id = student_id
        self.parent_window = parent_window
        self.current_quiz_widget = None

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(30, 20, 30, 30)
        self.layout.setSpacing(20)

        self.layout.addWidget(window_title_frame_style(" Επιλέξτε Μάθημα και Quiz", icon_path="icons/online-test-title.png"))

        self.course_list = QListWidget()
        self.course_list.itemClicked.connect(self.load_quizzes)
        self.layout.addWidget(self.course_list)

        self.quiz_list = QListWidget()
        self.layout.addWidget(self.quiz_list)

        # Κουμπιά δράσης
        buttons_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("Έναρξη Quiz")
        self.start_btn.clicked.connect(self.start_selected_quiz)
        buttons_layout.addWidget(self.start_btn)

        self.back_btn = QPushButton("← Πίσω")
        self.back_btn.clicked.connect(self.go_back)
        buttons_layout.addWidget(self.back_btn)
        
        self.layout.addLayout(buttons_layout)
        self.layout.addStretch()

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
        # Δημιουργία του Quiz widget με reference στο selection dialog
        self.current_quiz_widget = QuizExecutionDialog(student_id=self.student_id, quiz_id=quiz_id, parent=self.parent_window, selection_page=self)

        # Αν ο parent_window έχει content_stack, ενσωματώνουμε το quiz ως σελίδα
        if self.parent_window and hasattr(self.parent_window, 'content_stack'):
            self.parent_window.content_stack.addWidget(self.current_quiz_widget)
            self.parent_window.content_stack.setCurrentWidget(self.current_quiz_widget)
            # Κρύψουμε την επιλογή εδώ ώστε να μην είναι ορατή ενώ εκτελείται το quiz
            self.setVisible(False)

    def show_selection_again(self):
        """Επιστροφή στην επιλογή μετά το τέλος του quiz"""
        if self.current_quiz_widget:
            self.parent_window.content_stack.removeWidget(self.current_quiz_widget)
            self.current_quiz_widget.deleteLater()
            self.current_quiz_widget = None
        # Καθαρίζουμε τη λίστα quiz και ξαναφορτώνουμε τη λίστα μαθημάτων
        self.quiz_list.clear()
        self.setVisible(True)
        self.parent_window.content_stack.setCurrentWidget(self)

    def go_back(self):
        """Κλείνει την ενότητα και επιστρέφει στη λίστα μαθημάτων"""
        if self.current_quiz_widget:
            self.show_selection_again()
        elif self.parent_window and hasattr(self.parent_window, 'content_stack'):
            # Επιστροφή στη σελίδα 1 (Μαθήματα)
            self.parent_window.content_stack.setCurrentIndex(1)
