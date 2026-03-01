from PyQt5.QtWidgets import QVBoxLayout, QLabel, QListWidget, QMessageBox,QWidget,QPushButton,QHBoxLayout,QFrame
from db import get_available_courses_for_user,enroll_user_in_course
from styles_css.styles import students_stats_rounded_container,students_stats_rounded_sub_list

class EnrollPage(QWidget):
    def __init__(self, user_id, parent_window = 'CourseManagementWindow' ):
        super().__init__()
        self.user_id = user_id
        self.parent_window = parent_window #Κρατάμε αναφορά για να γυρνάμε πίσω

        #Κύριο layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(30,20,30,30)
        self.main_layout.setSpacing(20)

        #Τίτλος QLabel
        self.title = QLabel("Εγγραφή σε Νέο Μάθημα")
        self.title.setFixedHeight(40)
        self.title.setStyleSheet("font-size: 25px; font-weight: bold; color: #2c3e50;")
        self.main_layout.addWidget(self.title)

        #Δημιουργώ ένα container για να βαλω μεσα την λίστα με τα διαθεσιμα μαθηματα για εγγραφή
        self.list_container = QFrame()
        self.list_container.setStyleSheet(students_stats_rounded_container())#Χρησιμοποιώ το ίδιο QFrame στυλ όπως έκανα και στα στατιστικα του student
      
        #Layout για το εσωτερικό του container
        container_layout = QVBoxLayout(self.list_container)
        container_layout.setContentsMargins(10,10,10,10)

        # Δημιουργία και στυλ της λίστας
        self.course_list = QListWidget()
        self.course_list.setStyleSheet(students_stats_rounded_sub_list())#Χρησιμοποιώ το ίδιο QFrame στυλ όπως έκανα και στα στατιστικα του student
        self.load_courses()

        #Προσθήκη της λίστας μέσα στο layout του container
        container_layout.addWidget(self.course_list)

        #Προσθήκη του container στο κύριο layout της Σελίδας
        self.main_layout.addWidget(self.list_container)

        btn_layout = QHBoxLayout()
        btn_enroll = QPushButton("Επιβεβαίωση Εγγραφής")
        btn_enroll.clicked.connect(self.enroll)
        
        btn_layout.addWidget(btn_enroll)
        self.main_layout.addLayout(btn_layout)

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