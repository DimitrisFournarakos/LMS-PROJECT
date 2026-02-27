from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QListWidget,
    QPushButton, QHBoxLayout, QMessageBox
)
from db import get_all_courses


class AdminQuizCourseSelectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Επιλογή Μαθήματος για Δημιουργία Quiz")
        self.setGeometry(200, 200, 400, 300)

        self.selected_course_id = None

        self.layout = QVBoxLayout()

        self.course_list = QListWidget()
        self.load_courses()
        self.layout.addWidget(self.course_list)

        btn_layout = QHBoxLayout()

        self.select_btn = QPushButton("Επιλογή")
        self.select_btn.clicked.connect(self.select_course)

        self.cancel_btn = QPushButton("Άκυρο")
        self.cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(self.select_btn)
        btn_layout.addWidget(self.cancel_btn)

        self.layout.addLayout(btn_layout)
        self.setLayout(self.layout)

    def load_courses(self):
        try:
            courses = get_all_courses()
            for course in courses:
                self.course_list.addItem(f"{course[0]} - {course[1]}")
        except Exception as e:
            QMessageBox.critical(self, "Σφάλμα", f"Σφάλμα κατά τη φόρτωση μαθημάτων: {e}")

    def select_course(self):
        selected_item = self.course_list.currentItem()
        if selected_item:
            try:
                self.selected_course_id = int(selected_item.text().split(" - ")[0])
                self.accept()
            except ValueError:
                QMessageBox.warning(self, "Σφάλμα", "Δεν αναγνωρίστηκε το ID του μαθήματος.")
        else:
            QMessageBox.warning(self, "Προειδοποίηση", "Παρακαλώ επίλεξε ένα μάθημα.")

    def get_selected_course_id(self):
        return self.selected_course_id
