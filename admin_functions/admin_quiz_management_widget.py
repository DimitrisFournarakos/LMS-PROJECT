from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton, QMessageBox,QDialog
from db import get_quizzes_by_course, delete_quiz_by_id


class AdminQuizManagementWidget(QWidget):
    def __init__(self, course_id):
        super().__init__()
        self.course_id = course_id

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.label = QLabel(f"Διαχείριση Quiz για Μάθημα ID {course_id}")
        layout.addWidget(self.label)

        self.quiz_list = QListWidget()
        layout.addWidget(self.quiz_list)

        self.create_quiz_btn = QPushButton("Δημιουργία Quiz")
        self.create_quiz_btn.clicked.connect(self.create_quiz)
        layout.addWidget(self.create_quiz_btn)

        self.add_question_btn = QPushButton("Προσθήκη Ερώτησης")
        self.add_question_btn.clicked.connect(self.add_question)
        layout.addWidget(self.add_question_btn)

        self.delete_quiz_btn = QPushButton("Διαγραφή Quiz")
        self.delete_quiz_btn.clicked.connect(self.delete_quiz)
        layout.addWidget(self.delete_quiz_btn)

        self.load_quizzes()

    def load_quizzes(self):
        quizzes = get_quizzes_by_course(self.course_id)
        self.quiz_list.clear()

        if not quizzes:
            self.quiz_list.addItem("Δεν υπάρχουν quiz για διαχείριση.")
            self.delete_quiz_btn.setEnabled(False)
            self.add_question_btn.setEnabled(False)
        else:
            for quiz in quizzes:
                item = f"{quiz['quiz_id']} - {quiz['title']}"
                self.quiz_list.addItem(item)
            self.delete_quiz_btn.setEnabled(True)
            self.add_question_btn.setEnabled(True)

    def create_quiz(self):
        from course_management_window import ActualQuizCreationDialog
        dialog = ActualQuizCreationDialog(course_id=self.course_id, parent=self)
        if dialog.exec_():
            self.load_quizzes()

    def add_question(self):
        selected = self.quiz_list.currentItem()
        if not selected or selected.text() == "Δεν υπάρχουν quiz για διαχείριση.":
            QMessageBox.warning(self, "Προειδοποίηση", "Επίλεξε quiz για προσθήκη ερώτησης.")
            return
        quiz_id = int(selected.text().split(" - ")[0])

        from course_management_window import AddMultipleQuestionsDialog
        dialog = AddMultipleQuestionsDialog(quiz_id, parent=self)
        dialog.exec_()
        self.load_quizzes()

    def delete_quiz(self):
        selected = self.quiz_list.currentItem()
        if not selected or selected.text() == "Δεν υπάρχουν quiz για διαχείριση.":
            QMessageBox.warning(self, "Προειδοποίηση", "Επίλεξε quiz για διαγραφή.")
            return

        quiz_id = int(selected.text().split(" - ")[0])
        quiz_title = selected.text().split(" - ")[1]

        confirm = QMessageBox.question(
            self,
            "Επιβεβαίωση Διαγραφής",
            f"Είστε σίγουρος ότι θέλετε να διαγράψετε το quiz: '{quiz_title}';",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            try:
                delete_quiz_by_id(quiz_id)
                QMessageBox.information(self, "Επιτυχία", "Το quiz διαγράφηκε επιτυχώς.")
                self.load_quizzes()
            except Exception as e:
                QMessageBox.critical(self, "Σφάλμα", f"Σφάλμα κατά τη διαγραφή: {e}")
                from PyQt5.QtWidgets import QDialog, QVBoxLayout


class ActualQuizCreationDialog(QDialog):
    def __init__(self, course_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Διαχείριση Quiz")
        self.setMinimumWidth(500)
        self.course_id = course_id

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.management_widget = AdminQuizManagementWidget(course_id)
        layout.addWidget(self.management_widget)
