from PyQt5.QtWidgets import QVBoxLayout, QLabel, QListWidget, QMessageBox,QWidget,QPushButton,QHBoxLayout
from db import get_available_courses_for_user,enroll_user_in_course

class EnrollPage(QWidget):
    def __init__(self, user_id, parent_window = 'CourseManagementWindow' ):
        super().__init__()
        self.user_id = user_id
        self.parent_window = parent_window #Κρατάμε αναφορά για να γυρνάμε πίσω

        layout = QVBoxLayout(self)

        title = QLabel("Εγγραφή σε Νέο Μάθημα")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)

        self.course_list = QListWidget()
        self.load_courses()
        layout.addWidget(self.course_list)

        btn_layout = QHBoxLayout()
        btn_enroll = QPushButton("Επιβεβαίωση Εγγραφής")
        btn_enroll.clicked.connect(self.enroll)

        btn_back = QPushButton("Ακύρωση")
        btn_back.clicked.connect(lambda: self.parent_window.content_stack.setCurrentIndex(0))
        
        btn_layout.addWidget(btn_enroll)
        btn_layout.addWidget(btn_back)
        layout.addLayout(btn_layout)

    def load_courses(self):
        self.course_list.clear()
        available = get_available_courses_for_user(self.user_id)
        for c in available:
            self.course_list.addItem(f"{c[0]} - {c[1]}")

    def enroll(self):
        selected = self.course_list.currentItem()
        if selected:
            course_id = int(selected.text().split(" - ")[0])#Εξαγωγή του ID
            enroll_user_in_course(self.user_id, course_id)#Εγγραφή στη βάση δεδομένων

            self.parent_window.update_course_list()# Ενημέρωση του κεντρικού πίνακα (Index 0)

            self.load_courses() #Ανανέωση της ίδιας της λίστας εγγραφής ώστε να εξαφανιστεί το μάθημα που μόλις γράφτηκες
            self.parent_window.content_stack.setCurrentIndex(0)#Επιστροφή στην αρχική σελίδα
            
            QMessageBox.information(self, "Επιτυχία", "Η εγγραφή ολοκληρώθηκε!")
        else:
            QMessageBox.warning(self, "Προσοχή", "Παρακαλώ επιλέξτε ένα μάθημα από τη λίστα.")