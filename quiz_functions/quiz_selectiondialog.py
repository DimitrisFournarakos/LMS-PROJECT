from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QPushButton,
    QHBoxLayout, QMessageBox,QDialog
)
from db import get_all_courses

import sqlite3
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QPushButton, QMessageBox,
    QHBoxLayout
)


def get_all_courses():
    conn = sqlite3.connect("lms.db")
    cursor = conn.cursor()
    cursor.execute("SELECT course_id, name FROM courses ORDER BY name")
    courses = cursor.fetchall()
    conn.close()
    return courses


from PyQt5.QtWidgets import QWidget, QVBoxLayout, QListWidget, QPushButton, QHBoxLayout


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
        select_btn = QPushButton("Επιλογή")
        select_btn.clicked.connect(self.select_course)
        cancel_btn = QPushButton("Άκυρο")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(select_btn)
        btn_layout.addWidget(cancel_btn)

        self.layout.addLayout(btn_layout)
        self.setLayout(self.layout)

    def load_courses(self):
        courses = get_all_courses()
        for course in courses:
            self.course_list.addItem(f"{course[0]} - {course[1]}")

    def select_course(self):
        selected_item = self.course_list.currentItem()
        if selected_item:
            self.selected_course_id = int(selected_item.text().split(" - ")[0])
            self.accept()
        else:
            QMessageBox.warning(self, "Προσοχή", "Παρακαλώ επίλεξε ένα μάθημα.")

    def get_selected_course_id(self):
        return self.selected_course_id