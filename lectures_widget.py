import os,subprocess
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox,QFileDialog, QListWidget
from PyQt5.QtCore import Qt

class LecturesWidget(QWidget):
    def __init__(self, course_id, admin=False):
        super().__init__()
        self.course_id = course_id
        self.admin = admin

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.label = QLabel(f"Διαλέξεις Μαθήματος ID {self.course_id}")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        self.lectures_list = QListWidget()
        layout.addWidget(self.lectures_list)
        self.load_lectures()

        self.view_btn = QPushButton("📂 Προβολή Διαλέξεων")
        self.view_btn.clicked.connect(self.view_lectures)
        layout.addWidget(self.view_btn)

        self.add_btn = QPushButton("➕ Προσθήκη Διάλεξης")
        self.add_btn.clicked.connect(self.add_lecture)
        layout.addWidget(self.add_btn)

        if not self.admin:
            self.add_btn.setDisabled(True)

    def load_lectures(self):
        folder_path = os.path.join("lectures", f"course_{self.course_id}")
        self.lectures_list.clear()
        if os.path.exists(folder_path):
            for filename in os.listdir(folder_path):
                self.lectures_list.addItem(filename)

    def view_lectures(self):
        selected = self.lectures_list.currentItem()
        if not selected:
            QMessageBox.warning(self, "Προειδοποίηση", "Επίλεξε μια διάλεξη για προβολή.")
            return
        folder_path = os.path.join("lectures", f"course_{self.course_id}")
        file_path = os.path.join(folder_path, selected.text())
        if os.path.exists(file_path):
            try:
                if os.name == 'nt':
                    os.startfile(file_path)
                elif os.name == 'posix':
                    subprocess.run(["xdg-open", file_path])
            except Exception as e:
                QMessageBox.critical(self, "Σφάλμα", f"Αδυναμία ανοίγματος αρχείου: {e}")
        else:
            QMessageBox.warning(self, "Σφάλμα", "Το αρχείο δεν βρέθηκε.")

    def add_lecture(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Επιλέξτε διάλεξη (αρχείο)")
        if file_path:
            folder_path = os.path.join("lectures", f"course_{self.course_id}")
            os.makedirs(folder_path, exist_ok=True)
            filename = os.path.basename(file_path)
            target_path = os.path.join(folder_path, filename)
            try:
                with open(file_path, "rb") as source_file:
                    with open(target_path, "wb") as target_file:
                        target_file.write(source_file.read())
                QMessageBox.information(self, "Επιτυχία", "Η διάλεξη προστέθηκε με επιτυχία.")
                self.load_lectures()
            except Exception as e:
                QMessageBox.warning(self, "Σφάλμα", f"Σφάλμα κατά την προσθήκη διάλεξης: {str(e)}")
