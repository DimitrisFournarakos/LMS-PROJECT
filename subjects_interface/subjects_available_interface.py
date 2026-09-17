from PyQt5.QtWidgets import QVBoxLayout, QLabel,QWidget,QPushButton,QHBoxLayout,QFrame,QGraphicsOpacityEffect,QScrollArea
from PyQt5.QtCore import Qt,QSize,QTimer,QPropertyAnimation
from PyQt5.QtGui import QIcon,QPixmap
from db import get_available_courses_for_user,enroll_user_in_course
from styles_css.styles import students_stats_rounded_container, subjects_available_ScrollArea_style,subjects_available_course_list_style,subjects_available_back_btn_style,window_title_frame_style,students_courseItemFrame_style

class EnrollPage(QWidget):
    def __init__(self, user_id, parent_window = 'CourseManagementWindow' ):
        super().__init__()
        self.user_id = user_id
        self.parent_window = parent_window #Κρατάμε αναφορά για να γυρνάμε πίσω

        # Κύριο layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(30, 20, 30, 30)
        self.main_layout.setSpacing(20)

        self.main_layout.addWidget(window_title_frame_style(" Εγγραφή σε Νέο Μάθημα", icon_path="icons/register-subject-title.png"))

        # Δημιουργία Container για να βάλω μέσα τα items για τη λίστα με τα διαθέσιμα μαθήματα (με scroll)
        self.list_container = QFrame()
        self.list_container.setStyleSheet(students_stats_rounded_container()) #Χρησιμοποιώ το ίδιο style με τα στατιστικά για να είναι ομοιόμορφο

        container_layout = QVBoxLayout(self.list_container)
        container_layout.setContentsMargins(15, 15, 15, 15)


        # Δημιουργία και στυλ της λίστας με τα διαθέσιμα μαθήματα 
        #Δημιουργούμε ένα QScrollArea για να περιέχει τα μαθήματα, ώστε αν υπάρχουν πολλά, να μπορεί ο χρήστης να κάνει scroll.
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setStyleSheet(subjects_available_ScrollArea_style())

        # Widget που θα κρατάει τα items (αντικαθιστά το QListWidget)
        self.courses_widget = QWidget()
        self.courses_widget.setStyleSheet("background-color: transparent;")
        self.courses_layout = QVBoxLayout(self.courses_widget)
        self.courses_layout.setContentsMargins(0, 0, 0, 0)
        self.courses_layout.setSpacing(8)  # Κενό μεταξύ items
        self.courses_layout.addStretch()  # ΠUSH τα items πάνω

        self.scroll_area.setWidget(self.courses_widget)
        container_layout.addWidget(self.scroll_area)

        self.main_layout.addWidget(self.list_container)

        self.load_courses()

    def load_courses(self):
        """
        Φορτώνει τα διαθέσιμα μαθήματα από τη βάση δεδομένων και τα εμφανίζει στη λίστα.
        
        1. Καθαρίζει τα υπάρχοντα items από το layout (εκτός από το stretch στο τέλος)
        2. Ανακτά τα διαθέσιμα μαθήματα για τον χρήστη από τη βάση
        3. Δημιουργεί ένα QFrame για κάθε μάθημα με label και κουμπί εγγραφής
        4. Προσθέτει τα items στο layout με σωστή σειρά
        """
        # Καθαρισμός υπαρχόντων items
        while self.courses_layout.count() > 1:  # Κρατάμε το stretch στο τέλος
            child = self.courses_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        available = get_available_courses_for_user(self.user_id)

        for c in available:
            course_id = c[0]
            course_name = c[1]

            # Δημιουργία item ως QFrame (για να δουλεύει το border-radius),και στην κατάσταση hover και  στην selected.
            item_frame = QFrame()
            item_frame.setObjectName("courseItemFrame")
            item_frame.setFixedHeight(60) #Υψος κάθε σειράς της λίστας
            item_frame.setProperty("selected", False)  # Για το selected state
            item_frame.setStyleSheet(students_courseItemFrame_style())

            # Mouse click handling για selected state
            def on_frame_clicked(event, frame=item_frame):
                """
                Χειρίζεται το κλικ στο frame του μαθήματος για επιλογή/αποεπιλογή.
                
                1. Αποεπιλέγει όλα τα άλλα items που είναι επιλεγμένα (single selection)
                2. Toggle την επιλογή του τρέχοντος item
                3. Ενημερώνει το στυλ μέσω unpolish/polish για να εφαρμοστούν οι αλλαγές
                
                event: Το QMouseEvent που προκάλεσε την κλήση
                frame: Το QFrame που έγινε κλικ επάνω του για να το επιλέξουμε (προεπιλογή: το τρέχον item_frame)
                """
                # Αποεπιλογή όλων των άλλων items
                for i in range(self.courses_layout.count()):
                    widget = self.courses_layout.itemAt(i).widget()
                    if widget and widget != frame and widget.property("selected"):
                        widget.setProperty("selected", False)
                        widget.style().unpolish(widget)
                        widget.style().polish(widget)
                # Toggle το τρέχον item
                current_selected = frame.property("selected")
                frame.setProperty("selected", not current_selected)
                frame.style().unpolish(frame)
                frame.style().polish(frame)

            item_frame.mousePressEvent = on_frame_clicked

            row_layout = QHBoxLayout(item_frame)
            row_layout.setContentsMargins(15, 0, 15, 0)

            label = QLabel(course_name)
            label.setStyleSheet("font-size: 16px; color: #2f3640; font-weight: 500; background: transparent; border: none;")

            # Κουμπί με Icon
            btn_enroll = QPushButton()
            btn_enroll.setIcon(QIcon("icons/register-subject.png"))
            btn_enroll.setIconSize(QSize(30, 30))
            btn_enroll.setFixedSize(35, 35)
            btn_enroll.setCursor(Qt.PointingHandCursor)
            btn_enroll.setStyleSheet(subjects_available_back_btn_style())

            btn_enroll.clicked.connect(lambda _, course=course_id, frame=item_frame: self.enroll(course, frame))

            row_layout.addWidget(label)
            row_layout.addStretch()
            row_layout.addWidget(btn_enroll)

            # Προσθήκη στο layout (πριν το stretch)
            self.courses_layout.insertWidget(self.courses_layout.count() - 1, item_frame)

    def enroll(self, course_id, item_frame):
        """
        Εγγράφει τον χρήστη στο επιλεγμένο μάθημα και εμφανίζει οπτική επιβεβαίωση.
        
        1. Κάνει την εγγραφή στη βάση δεδομένων
        2. Απενεργοποιεί το κουμπί εγγραφής και το κάνει γκρι
        3. Εμφανίζει ένα checkmark με fade-in animation δίπλα στο όνομα του μαθήματος
        4. Ενημερώνει τον κεντρικό πίνακα μαθημάτων του χρήστη
        5. Μετά από 1.5 δευτερόλεπτα ανανεώνει τη λίστα και επιστρέφει στην αρχική σελίδα
        
        course_id: Το ID του μαθήματος στο οποίο γίνεται η εγγραφή
        item_frame: Το QFrame που αντιπροσωπεύει τη σειρά του μαθήματος στη λίστα
        """
        enroll_user_in_course(self.user_id, course_id) #Εγγραφή του χρήστη στο μάθημα (στη βάση δεδομένων)
        
        # Το item_frame είναι το QFrame που περιέχει το layout(label + button) για το συγκεκριμένο μάθημα.
        row_layout = item_frame.layout()
        
        # Απενεργοποίηση του κουμπιού εγγραφής,όταν πατηθεί και εμφανιστεί το checkmark, ώστε να μην μπορεί να ξαναπατηθεί.
        for i in range(row_layout.count()):
            widget = row_layout.itemAt(i).widget()
            if isinstance(widget, QPushButton):
                widget.setEnabled(False)
                widget.setStyleSheet("background-color: #bdc3c7; color: #ecf0f1; border-radius: 12px; border: none;")
                break
        
        # Δημιουργία του checkmark
        checkmark_label = QLabel()
        pixmap = QPixmap("icons/checkmark.png")
        scaled_pixmap = pixmap.scaled(28, 28, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        checkmark_label.setPixmap(scaled_pixmap)
        checkmark_label.setStyleSheet("background: transparent; border: none;")
        checkmark_label.setFixedWidth(40)

        # Προσθήκη Εφέ Διαφάνειας για το animation
        opacity_effect = QGraphicsOpacityEffect(checkmark_label)
        checkmark_label.setGraphicsEffect(opacity_effect)
        row_layout.insertWidget(1, checkmark_label)  # Τοποθέτηση δίπλα στο κείμενο (position 1)

        # Animation εμφάνισης (Fade In)
        self.anim = QPropertyAnimation(opacity_effect, b"opacity")
        self.anim.setDuration(900)  # 0.9 Δευτερόλεπτα
        self.anim.setStartValue(0)
        self.anim.setEndValue(1)
        self.anim.start()

        # Μικρό "πήδημα": θα κουνηθεί λίγο προς τα δεξιά
        checkmark_label.setContentsMargins(10, 0, 0, 0)  # Ξεκινάει με margin

        self.parent_window.update_course_list()  # Ενημέρωση του κεντρικού πίνακα (Index 0)

        # Περίμενε 1.5 δευτερόλεπτα και μετά ανανέωσε τη λίστα (χωρίς να αλλάξει σελίδα)
        QTimer.singleShot(1400, lambda: (
            self.load_courses(),  # Ανανέωση της λίστας εγγραφής ώστε να εξαφανιστεί το μάθημα που μόλις γράφτηκε
        ))
       
        
        
       
