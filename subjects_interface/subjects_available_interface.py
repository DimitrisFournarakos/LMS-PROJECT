from PyQt5.QtWidgets import QVBoxLayout, QLabel, QListWidget, QMessageBox,QWidget,QPushButton,QHBoxLayout,QFrame,QListWidgetItem,QGraphicsOpacityEffect
from PyQt5.QtCore import Qt,QSize,QTimer,QPropertyAnimation
from PyQt5.QtGui import QIcon,QPixmap
from db import get_available_courses_for_user,enroll_user_in_course
from styles_css.styles import students_stats_rounded_container,subjects_available_course_list_style,subjects_available_back_btn_style

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
        self.course_list.setStyleSheet(subjects_available_course_list_style())#Χρησιμοποιώ το ίδιο QFrame στυλ όπως έκανα και στα στατιστικα του student
        self.load_courses()

        #Προσθήκη της λίστας μέσα στο layout του container
        container_layout.addWidget(self.course_list)

        #Προσθήκη του container στο κύριο layout της Σελίδας
        self.main_layout.addWidget(self.list_container)

    def load_courses(self):
        self.course_list.clear()
        available = get_available_courses_for_user(self.user_id)
        
        for c in available:
            course_id = c[0]
            course_name = c[1]

            #Δημιουργούμε το item της λίστας
            item = QListWidgetItem(self.course_list)
            item.setSizeHint(QSize(0, 60)) #Ύψος κάθε σειράς

            #Δημιουργούμε ένα απλό QWidget που θα κρατάει το όνομα και το κουμπί
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(15, 0 ,15, 0)

            label = QLabel(course_name)
            label.setStyleSheet("font-size: 16px; color: #2f3640; font-weight: 500; background: transparent; border: none;")

            # Κουμπί με Icon
            btn_enroll = QPushButton()
            btn_enroll.setIcon(QIcon("icons/register-subject.png"))
            btn_enroll.setIconSize(QSize(30,30))#Μέγεθος icon κουμπιού
            btn_enroll.setFixedSize(35, 35)#Μέγεθος background κουμπιού
            btn_enroll.setCursor(Qt.PointingHandCursor)
            btn_enroll.setStyleSheet(subjects_available_back_btn_style())
            
            btn_enroll.clicked.connect(lambda _, course_id = course_id, item = item : self.enroll(course_id,item))

            row_layout.addWidget(label)
            row_layout.addStretch()
            row_layout.addWidget(btn_enroll)

            #Προσθέτουμε το widget στο item
            self.course_list.addItem(item)
            self.course_list.setItemWidget(item,row_widget)


    def enroll(self,course_id,item):      
        enroll_user_in_course(self.user_id, course_id)#Εγγραφή στη βάση δεδομένων

        # Παίρνω το row_widget που περιέχει το label και το button
        row_widget = self.course_list.itemWidget(item)
        row_layout = row_widget.layout()
        
        #Δημιουργία του checkmark
        checkmark_label = QLabel()
        pixmap = QPixmap("icons/checkmark.png")
        scaled_pixmap = pixmap.scaled(28, 28, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        checkmark_label.setPixmap(scaled_pixmap)
        checkmark_label.setStyleSheet("background: transparent; border: none;")
        checkmark_label.setFixedWidth(40)

        #Προσθήκη Εφέ Διαφάνειας για το animation
        opacity_effect = QGraphicsOpacityEffect(checkmark_label)
        checkmark_label.setGraphicsEffect(opacity_effect)
        row_layout.insertWidget(1,checkmark_label)# Τοποθέτηση δίπλα στο κείμενο (position 1)

        # Animation εμφάνισης (Fade In)
        self.anim = QPropertyAnimation(opacity_effect, b"opacity")
        self.anim.setDuration(900) # 0.9 Δευτερόλεπτα
        self.anim.setStartValue(0)
        self.anim.setEndValue(1)
        self.anim.start()

        #Μικρό "πήδημα": θα κουνηθεί λίγο προς τα δεξιά
        checkmark_label.setContentsMargins(10,0,0,0) # Ξεκινάει με margin

        self.parent_window.update_course_list()# Ενημέρωση του κεντρικού πίνακα (Index 0)

        # Περίμενε 1.5 δευτερόλεπτα και μετά ανανέωσε τη λίστα
        QTimer.singleShot(1400, lambda:(
            self.load_courses(), #Ανανέωση της ίδιας της λίστας εγγραφής ώστε να εξαφανιστεί το μάθημα που μόλις γράφτηκες
            self.parent_window.content_stack.setCurrentIndex(0)#Επιστροφή στην αρχική σελίδα
        ))
       
        
        
       
