import sqlite3,os,subprocess
from styles_css import styles
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame,QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,QMessageBox, QFileDialog, QLabel, QDialog,QMessageBox, QFileDialog, QLabel, QDialog,QHeaderView,QStackedWidget)
from PyQt5.QtCore import Qt,QSize,QPropertyAnimation,QEvent
from PyQt5.QtGui import QPixmap, QPainter,QIcon,QCursor
from db import (get_enrolled_courses,add_question_to_quiz,create_course, update_course, get_all_courses, delete_course,unenroll_user_from_course)
from student_functions.student_quiz_selection_dialog import StudentQuizSelectionDialog
from student_functions.student_quiz_stats_page import StudentQuizStatsPage
from quiz_functions.quiz_selectiondialog import AdminQuizCourseSelectionDialog
from subjects_interface.subjects_available_interface import EnrollPage

class TableWithBackground(QTableWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bg_pixmap = QPixmap('icons/background_subjects_interface.jpg')            
        self.horizontalHeader().setStretchLastSection(True)#Εμφανίζουμε τους τίτλους των στηλών(ID,Περιγραφή,κλπ.)
        self.verticalHeader().setVisible(False) # Κρύβουμε τους αριθμούς αριστερά

    def resizeEvent(self, event):#Όταν αλλάζει το μέγεθος του πίνακα, ανανεώνουμε την κλίμακα της εικόνας background για να καλύπτει όλο το πίνακα 
        super().resizeEvent(event)
        if not self.bg_pixmap.isNull():
            w = self.viewport().width()
            h = self.viewport().height()
            self.scaled_pixmap = self.bg_pixmap.scaled(
                w, h, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        self.viewport().update()

    def paintEvent(self, event):#Τοποθετώ την εικόνα background πίσω από τα δεδομένα του πίνακα
        painter = QPainter(self.viewport())
        if hasattr(self, 'scaled_pixmap') and self.scaled_pixmap: #Ελέγχει αν υπάρχει η εικόνα και αν έχει ήδη κλιμακωθεί σωστά στο μέγεθος του παραθύρου
            x = (self.viewport().width() - self.scaled_pixmap.width()) // 2    #ΚΕΝΤΡΑΡΙΣΜΑ ΕΙΚΟΝΑΣ
            y = (self.viewport().height() - self.scaled_pixmap.height()) // 2  #ΚΕΝΤΡΑΡΙΣΜΑ ΕΙΚΟΝΑΣ
            painter.drawPixmap(x, y, self.scaled_pixmap)
        super().paintEvent(event)

       
class CourseManagementWindow(QWidget):
    def __init__(self, user_id, admin=False):
        super().__init__()
        self.user_id = user_id
        self.admin = admin
        self.setWindowTitle("Διαχείριση Μαθημάτων")
        self.setGeometry(100, 100, 1100, 650)                
        self.setStyleSheet(styles.get_main_window_style())

        self.init_ui()

    def init_ui(self):
        self.outer_layout = QVBoxLayout(self)
        self.outer_layout.setContentsMargins(0, 0, 0, 0)
        self.outer_layout.setSpacing(0)

        self.setMouseTracking(True) # Ενεργοποίηση στο κεντρικό παράθυρο,του hover για το menu_btn
        self.installEventFilter(self)# Προσθήκη αυτού για να παρακολουθεί όλο το παράθυρο
        
        # TOP BAR - Το κουμπί μένει εδώ για να μην χάνεται ποτέ
        self.top_bar = QFrame()
        self.top_bar.setMouseTracking(True)#Για να μπορεί να παρακολουθεί το ποντίκι και να στείλει το event για να ανοιξει το μενου αν είναι κλειστό
        self.top_bar.setFixedHeight(50)
        self.top_bar.setStyleSheet("background-color: #34405e; border-bottom: 1px solid #2c3e50;")
        top_bar_layout = QHBoxLayout(self.top_bar)
        top_bar_layout.setContentsMargins(10, 0, 10, 0)

        self.menu_btn = QPushButton()
        self.menu_btn.setIcon(QIcon("icons/menu.png"))
        self.menu_btn.setIconSize(QSize(30, 30))
        self.menu_btn.setFixedSize(40, 40)
        self.menu_btn.setCursor(Qt.PointingHandCursor)
        self.menu_btn.setStyleSheet("background: transparent; border: none;")
        self.menu_btn.installEventFilter(self)

        top_bar_layout.addWidget(self.menu_btn)
        top_bar_layout.addStretch()
        self.outer_layout.addWidget(self.top_bar)

        # Κύριο οριζόντιο layout (Sidebar | Content)
        self.main_content_layout = QHBoxLayout()

        # --- SIDEBAR CONTAINER ---
        self.sidebar_container = QFrame()
        self.sidebar_container.setStyleSheet(styles.sidebar_style())
        self.sidebar_vbox = QVBoxLayout(self.sidebar_container)
        self.sidebar_vbox.setContentsMargins(0, 0, 0, 0) #Για να καλυπτει όλη την επιφάνεια,να είναι κολλημένο και με το content
        self.sidebar_vbox.setSpacing(0)

        # 1. ΣΤΑΘΕΡΟ HEADER (Icon + Title) - Αυτό δεν κλείνει ποτέ - Κεντραρισμένο
        self.sidebar_header = QFrame()
        self.sidebar_header.setFixedHeight(70)
        self.sidebar_header.setStyleSheet("background-color: #1a252f; border-bottom: 1px solid #34495e;")
        
        # Χρησιμοποιούμε κάθετο layout για να μπει ο τίτλος ΚΑΤΩ από το κουμπί
        header_layout = QVBoxLayout(self.sidebar_header)

        #Δημιουργία οριζόντιου layout ΜΟΝΟ για το κουμπί ώστε να κεντραριστεί οριζόντια
        btn_container = QHBoxLayout()
        btn_container.addStretch() # Σπρώχνει από αριστερά

        # Ο Τίτλος
        self.sidebar_title_label = QLabel("MENU")
        self.sidebar_title_label.setAlignment(Qt.AlignCenter)
        self.sidebar_title_label.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        
        header_layout.addLayout(btn_container)
        header_layout.addWidget(self.sidebar_title_label)
        
        self.sidebar_vbox.addWidget(self.sidebar_header)

        # 2. ΠΤΥΣΣΟΜΕΝΟ BODY (Τα κουμπιά των επιλογών)
        self.sidebar_body = QFrame()
        self.sidebar_body_layout = QVBoxLayout(self.sidebar_body)
        self.sidebar_body_layout.setContentsMargins(15, 5, 5, 15)
        
        # Προσθήκη των κουμπιών στο πτυσσόμενο μέρος
        self.setup_sidebar_buttons_to_layout(self.sidebar_body_layout)
        
        self.sidebar_vbox.addWidget(self.sidebar_body,1)# Το "1" αναγκάζει το body να πιάσει όλο το ύψος
       

        # --- CONTENT AREA (Δεξί Panel) ---
        self.content_stack = QStackedWidget()
        self.create_course_list_page() # Σελίδα 0: Λίστα Μαθημάτων

        if self.admin:# Index 1: Admin Tools (Αν είναι student, βάζουμε ένα κενό widget για να κρατήσουμε τη θέση)
            self.create_admin_tools_page()
        else:
            empty_widget = QWidget()
            self.content_stack.addWidget(empty_widget)#Κρατάει το Index 1

        if not self.admin:# Σελίδα 2: Εγγραφή (για Student)
            self.enroll_page = EnrollPage(self.user_id,self)
            self.content_stack.addWidget(self.enroll_page) # Αυτό θα είναι τώρα το Index 2
        else:# Αν είναι admin, βάζω πάλι ένα κενό widget για να μην μπερδευτούν τα index αν προστεθεί κάτι μετά
            self.content_stack.addWidget(QWidget())

        self.stats_page = StudentQuizStatsPage(self.user_id,self)#Σελίδα 3: Στατιστικά (Για όλους ή μονο για student)
        self.content_stack.addWidget(self.stats_page)

        # Σύνθεση κύριου layout
        self.main_content_layout.addWidget(self.sidebar_container)
        self.main_content_layout.addWidget(self.content_stack, 1)

        self.outer_layout.addLayout(self.main_content_layout)

        #Εφαρμόζουμε το event_filter για να ακούει οτι υπάρχει στο top_bar,content_stack για να συμβάλει στο auto-close-menu
        self.apply_filter_to_children(self.content_stack)
        self.apply_filter_to_children(self.top_bar)

    def apply_filter_to_children(self, widget):#Συνάρτηση για να ακούει το event filter οτιδηποτε πατησουμε στο content-area και να γινει το auto-close-menu
        # Εγκαθιστά τον filter στο ίδιο το widget
        widget.installEventFilter(self)
        # Και επαναληπτικά σε όλα τα παιδιά του (κουμπιά, inputs, κλπ)
        for child in widget.findChildren(QWidget):
            child.installEventFilter(self)
    
    def showEvent(self, event):
        super().showEvent(event)

        # Αρχικά κλειστό sidebar
        self.sidebar_visible = False
        self.sidebar_header.hide() #Κρύβω το header,body για να υπάρχει μόνο το background-color της λωρίδας του sidebar_conteiner
        self.sidebar_body.hide()
        self.sidebar_container.setMinimumWidth(70)
        self.sidebar_container.setMaximumWidth(70)

    def eventFilter(self, obj, event):
        # Όταν το ποντίκι μπει πάνω στο menu button auto-open-menu
        if obj == self.menu_btn and event.type() == QEvent.Enter:
            if not self.sidebar_visible:
                self.toggle_sidebar()
            return True
        
        # Auto-Close: MouseButtonPress σε οποιοδήποτε αντικείμενο ΕΚΤΟΣ sidebar
        if event.type() == QEvent.MouseButtonPress:
            if self.sidebar_visible:
                click_pos = self.mapFromGlobal(QCursor.pos())#Μετατρέπουμε τη θέση του κλικ σε global και μετά σε τοπική,ως προς το CourseManagementWindow (self)                

                if click_pos.x() > self.sidebar_container.width(): # Αν το κλικ έγινε δεξιά από το όριο του sidebar
                    self.toggle_sidebar()
                    return False# Επιστρέφουμε False για να εκτελεστεί κανονικά το κλικ στο κουμπί ή στο input που πατήθηκε

        return super().eventFilter(obj, event)

    def toggle_sidebar(self):
        if hasattr(self, 'animation') and self.animation.state() == QPropertyAnimation.Running:
            return #Αν ήδη τρέχει το animation τότε προχώρα

        current_width = self.sidebar_container.width()

        if current_width == 70:
            end_width = 250
            self.sidebar_visible = True
            self.sidebar_header.show()
            self.sidebar_body.show()
        else:
            end_width = 70
            self.sidebar_visible = False
            self.sidebar_header.hide()
            self.sidebar_body.hide()

        self.animation = QPropertyAnimation(self.sidebar_container, b"minimumWidth")
        self.animation.setDuration(200)
        self.animation.setStartValue(current_width)
        self.animation.setEndValue(end_width)
        self.animation.start()

    def on_animation_finished(self):
        if self.sidebar_visible:
            self.sidebar_body.show()
            self.sidebar_title_label.show()
            self.sidebar_header.setStyleSheet("background-color: #1a252f; border-bottom: 1px solid #34495e;")
        
    def setup_sidebar_buttons_to_layout(self,sidebar_body_layout):
        """Βοηθητική συνάρτηση για να τοποθετήσουμε τα κουμπιά στο νέο layout"""
        self.btn_courses = QPushButton(" Μαθήματα")
        self.btn_courses.setIcon(QIcon("icons/education.png"))
        self.btn_courses.setIconSize(QSize(15,15))
        self.btn_courses.setFixedSize(40,40)
        self.btn_courses.setFixedWidth(250)
        self.btn_courses.clicked.connect(lambda: self.content_stack.setCurrentIndex(0))
        sidebar_body_layout.addWidget(self.btn_courses)

        if self.admin:
            self.btn_admin = QPushButton(" Διαχείριση Quiz")
            self.btn_admin.setIcon(QIcon("icons/online-test.png"))
            self.btn_admin.setIconSize(QSize(15,15))
            self.btn_admin.setFixedSize(40,40)
            self.btn_admin.setFixedWidth(250)
            self.btn_admin.clicked.connect(lambda: self.content_stack.setCurrentIndex(1))
            self.sidebar_body_layout.addWidget(self.btn_admin)
        else:
            self.btn_enroll = QPushButton(" Εγγραφή")
            self.btn_enroll.setIcon(QIcon("icons/edit.png"))
            self.btn_enroll.setIconSize(QSize(15,15))
            self.btn_enroll.setFixedSize(40,40)
            self.btn_enroll.setFixedWidth(250)
            self.btn_enroll.clicked.connect(lambda: self.content_stack.setCurrentIndex(2))
            self.sidebar_body_layout.addWidget(self.btn_enroll)

        self.btn_stats = QPushButton(" Στατιστικά")
        self.btn_stats.setIcon(QIcon("icons/stats.png"))
        self.btn_stats.setIconSize(QSize(15,15))
        self.btn_stats.setFixedSize(40,40)
        self.btn_stats.setFixedWidth(250)
        self.btn_stats.clicked.connect(lambda: self.content_stack.setCurrentIndex(3))
        self.sidebar_body_layout.addWidget(self.btn_stats)
        
        self.sidebar_body_layout.addStretch(1)# Αυτό το stretch σπρώχνει ό,τι ακολουθεί στο κάτω μέρος του sidebar
        self.apply_filter_to_children(sidebar_body_layout)
        
        back_btn_layout = QHBoxLayout()
        back_btn_layout.addStretch(1) # Το stretch στην αρχή του οριζόντιου layout σπρώχνει το κουμπί δεξιά

        self.back_btn = QPushButton("Αποσύνδεση")
        self.back_btn.setIcon(QIcon("icons/sign-out.png"))
        self.back_btn.setIconSize(QSize(15,15))
        self.back_btn.setFixedSize(40,40)
        self.back_btn.setFixedWidth(250)
        self.back_btn.clicked.connect(self.go_back)

        back_btn_layout.addWidget(self.back_btn)
        back_btn_layout.addStretch(1)
        self.apply_filter_to_children(back_btn_layout)


        self.sidebar_body_layout.addLayout(back_btn_layout)

    def create_course_list_page(self):
        """Σελίδα 0: Λίστα Μαθημάτων (Κοινή για Admin και Student)"""
        page = QWidget()
        layout = QVBoxLayout(page)

        title = QLabel("Τα μαθήματά μου" if not self.admin else "Πίνακας Ελέγχου Μαθημάτων")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 10px; color: #2c3e50;")
        layout.addWidget(title)

        self.table = TableWithBackground()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["Όνομα", "Περιγραφή", "Κατηγορία", "Εκπαιδευτής", "Έναρξη", "Λήξη", "Ενέργειες"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) #Οι στήλες του πίνακα θα προσαρμόζονται αυτόματα στο διαθέσιμο πλάτος του πίνακα, ώστε να καλύπτουν όλο το πλάτος χωρίς να αφήνουν κενά ή να δημιουργούν οριζόντιο scrollbar
        self.table.cellClicked.connect(self.on_table_item_clicked)#Όταν ο χρήστης κάνει κλικ σε ένα κελί του πίνακα, καλείται η μέθοδος on_table_item_clicked που θα χειρίζεται την εμφάνιση των πληροφοριών του μαθήματος στα πεδία κειμένου για τον Admin ή θα ανοίγει τις διαλέξεις για τον Student
        layout.addWidget(self.table)

        self.content_stack.addWidget(page) #Προσθέτουμε αυτή τη σελίδα στη στοίβα του content_stack, ώστε να μπορεί να εμφανιστεί όταν πατηθεί το κουμπί "Μαθήματα" στο sidebar
        self.update_course_list() #Φορτώνουμε τα μαθήματα από τη βάση δεδομένων και τα εμφανίζουμε στον πίνακα κάθε φορά που δημιουργείται αυτή η σελίδα, ώστε να είναι πάντα ενημερωμένη με τις τελευταίες αλλαγές (π.χ. νέες εγγραφές, προσθήκη/διαγραφή μαθημάτων από τον Admin)

    def create_admin_tools_page(self):
        """Σελίδα 1: Φόρμα Διαχείρισης μόνο για Admin"""
        page = QWidget()
        layout = QVBoxLayout(page)

        title = QLabel("Επεξεργασία Μαθημάτων & Διαχείριση Quiz")
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)

        form_container = QFrame()#Φτιάχνω ένα container-πλαίσιο για να βάλω τα πεδία κειμένου("όνομα,περιγραφή κλπ.")
        form_container.setStyleSheet("background: white; border-radius: 10px; padding: 20px;")
        form_layout = QVBoxLayout(form_container)#Τοποθετώ τα πεδία κειμένου μέσα στο form_container για να έχουν λευκό φόντο και να ξεχωρίζουν από το υπόλοιπο περιεχόμενο της σελίδας

        #Πεδία Εισαγωγής για τα στοιχεία του μαθήματος που θέλει να προσθέσει ή να ενημερώσει ο Admin
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Όνομα Μαθήματος")
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Περιγραφή Μαθήματος")
        self.category_input = QLineEdit()
        self.category_input.setPlaceholderText("Κατηγορία")
        self.instructor_input = QLineEdit()
        self.instructor_input.setPlaceholderText("Καθηγητής")
        self.start_date_input = QLineEdit()
        self.start_date_input.setPlaceholderText("Έναρξη (DD/MM/YYYY)")
        self.end_date_input = QLineEdit()
        self.end_date_input.setPlaceholderText("Λήξη (DD/MM/YYYY)")

        for inputs in [self.name_input, self.description_input, self.category_input, self.instructor_input, self.start_date_input, self.end_date_input]:
            form_layout.addWidget(inputs)

        #Buttons Λειτουργιών
        self.add_course_btn = QPushButton("➕ Προσθήκη Μαθήματος")
        self.add_course_btn.clicked.connect(self.add_course)

        self.delete_course_btn = QPushButton("🗑️ Διαγραφή Μαθήματος")
        self.delete_course_btn.clicked.connect(self.delete_course)
        
        self.quiz_btn = QPushButton("📝 Δημιουργία Νέου Quiz")
        self.quiz_btn.clicked.connect(self.open_create_quiz_course_selection)


        form_layout.addWidget(self.add_course_btn)
        form_layout.addWidget(self.delete_course_btn)
        form_layout.addWidget(self.quiz_btn)

        layout.addWidget(form_container)
        layout.addStretch()
        self.content_stack.addWidget(page) 

    
    def on_table_item_clicked(self, row, col):
        # Όταν ο Admin κάνει κλικ στον πίνακα, τον μεταφέρουμε αυτόματα στη σελίδα επεξεργασίας(CurrentIndex(1))
        if self.admin:
            self.content_stack.setCurrentIndex(1)

            item_name = self.table.item(row, 0)# Στήλη 0: Περιέχει το Όνομα και το Κρυφό ID (UserRole)
            course_id = item_name.data(Qt.UserRole)# Παίρνουμε το σωστό ID για το update

            self.name_input.setText(item_name.text())
            self.description_input.setText(self.table.item(row, 1).text())
            self.category_input.setText(self.table.item(row, 2).text())
            self.instructor_input.setText(self.table.item(row, 3).text())
            self.start_date_input.setText(self.table.item(row, 4).text())
            self.end_date_input.setText(self.table.item(row, 5).text())

            self.add_course_btn.setText("📝 Ενημέρωση Μαθήματος")

            try: 
                self.add_course_btn.clicked.disconnect()#Αποεπιλεγουμε το μαθημα που ειχαμε επιλεξει να αλλαξουμε-ενημέρωση
            except: 
                pass #"Αν δεν έχουμε τίποτα να αποσυνδέσουμε, εντάξει, απλά προχωράμε"

            self.add_course_btn.clicked.connect(lambda: self.update_course(course_id))#lambda = "Όταν σε πατήσουν, κάλεσε τη συνάρτηση update_course για το συγκεκριμένο ID μαθήματος που μόλις κάναμε κλικ στον πίνακα"

    def update_course_list(self):
        if self.admin:
            courses = get_all_courses()
        else:
            courses = get_enrolled_courses(self.user_id)
    
        self.table.setRowCount(len(courses))#ο πίνακας δημιουργεί ακριβώς τόσες γραμμές όσες είναι και τα μαθήματα που βρέθηκαν,αναλογα την ιδιότητα μας

        for row_index, course in enumerate(courses):
            data_to_show = [course[1], course[2], course[3], course[4], course[6], course[7]] #Παραλείπουμε το course[5] που είναι το instructor_id και δεν θέλουμε να εμφανίζεται στον πίνακα,ετσι εχω φτιάξει την δομή του πίνακα courses στο db.py
            for col_idx, data in enumerate(data_to_show):                                                #Τα courses[],είναι οι στήλες ID,Όνομα,Πειγραφή κλπ.
                #Το διπλό for-loop rows,,cols μετατρέπει κάθε πληροφορία σε QTableWidgetItem  
                item = QTableWidgetItem(str(data))

                if col_idx == 0:
                    item.setData(Qt.UserRole, course[0]) #Αν είμαστε στην πρώτη στήλη,αποθηκεύω κρυφά το course[0],που ειναι το id που θέλω
                
                item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable) #κάνει τα κελιά "μόνο για ανάγνωση" μέσα στον πίνακα,ο χρήστης μπορεί μόνο να τα επιλέξει αλλά όχι να γράψει μέσα τους
                self.table.setItem(row_index, col_idx, item)

            # Container για δύο κουμπιά
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(35, 0, 35, 0) #setContentsMargins(left, top, right, bottom)
            actions_layout.setSpacing(120) #Απόσταση μεταξύ των κουμπιών

            #Κουμπί Διαλέξεων
            lecture_btn = QPushButton("📂")
            lecture_btn.setToolTip("Διαλέξεις")
            lecture_btn.setFixedSize(32,32)
            lecture_btn.clicked.connect(lambda _, course_id = course[0]: self.open_lectures(course_id))

            #Κουμπί Απεγγραφής (μόνο για students)
            if not self.admin:
                unenroll_btn = QPushButton("✖️")
                unenroll_btn.setToolTip("Απεγγραφή")
                unenroll_btn.setFixedSize(32,32)
                unenroll_btn.setStyleSheet("background: #e74c3c; color: white; border: none; border-radius: 3px;")
                unenroll_btn.clicked.connect(lambda _, course_id=course[0]: self.unenroll_from_course(course_id))
                actions_layout.addWidget(lecture_btn)
                actions_layout.addWidget(unenroll_btn)
            else:
                actions_layout.addWidget(lecture_btn)

            actions_layout.addStretch()
            self.table.setCellWidget(row_index,6,actions_widget)


        # Εφαρμογή στυλ κεφαλίδας και ρύθμιση για να πιάνουν όλο το πλάτος
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setStyleSheet(styles.get_table_header_style())

    
    def enroll_in_course(self):
        dialog = EnrollPage(self.user_id, self)
        dialog.exec_()
        self.update_course_list()

    def unenroll_from_course(self, course_id):
        success = unenroll_user_from_course(self.user_id, course_id)

        if success:
            self.update_course_list()  # Ανανέωση enrolled courses
            if hasattr(self, 'enroll_page'):  # Αν υπάρχει η σελίδα εγγραφής, ανανεώνουμε και εκείνη
                self.enroll_page.load_courses()

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def open_quiz_stats_dialog(self):
        from admin_functions.admin_quiz_stats_dialog import AdminTotalQuizStatsDialog
        dialog = AdminTotalQuizStatsDialog(self)
        dialog.exec_()

    def open_student_stats(self):
        from student_functions.student_quiz_stats_page import StudentQuizStatsDialog
        dialog = StudentQuizStatsDialog(self.user_id, self)
        dialog.exec_()

    def add_course(self):
        name = self.name_input.text().strip()
        description = self.description_input.text().strip()
        category = self.category_input.text().strip()
        instructor = self.instructor_input.text().strip()
        start_date = self.start_date_input.text().strip()
        end_date = self.end_date_input.text().strip()

        if not all([name, description, category, instructor, start_date, end_date]):
            QMessageBox.warning(self, "Προειδοποίηση", "Παρακαλώ συμπληρώστε όλα τα πεδία.")
            return

        create_course(name, description, category, instructor, start_date, end_date)
        self.update_course_list()
        self.clear_inputs()

    def delete_course(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Προειδοποίηση", "Παρακαλώ επιλέξτε ένα μάθημα για διαγραφή.")
            return

        item = self.table.item(row, 0)# Παίρνουμε το αντικείμενο της πρώτης στήλης
        course_id = item.data(Qt.UserRole)# Ανακτούμε το κρυφό ID που αποθηκεύσαμε με το UserRole

        reply = QMessageBox.question(self, 'Επιβεβαίωση', f'Είστε βέβαιοι ότι θέλετε να διαγράψετε το μάθημα με ID {course_id};',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No) #Την δεύτερη φορά που βάζουμε την επιλογή No(QMessageBox.No) την εχουμε ουσιαστικά προεπιλέξει και με ενα enter επιλεγουμε το Οχι

        if reply == QMessageBox.Yes:
            delete_course(course_id)
            self.update_course_list()

    def update_course(self, course_id):
        name = self.name_input.text().strip()#.strip()Αφαιρεί όλους τους κενούς χαρακτήρες (whitespace) από την αρχή και το τέλος ενός string
        description = self.description_input.text().strip()
        category = self.category_input.text().strip()
        instructor = self.instructor_input.text().strip()
        start_date = self.start_date_input.text().strip()
        end_date = self.end_date_input.text().strip()

        if not all([name, description, category, instructor, start_date, end_date]):
            QMessageBox.warning(self, "Προειδοποίηση", "Παρακαλώ συμπληρώστε όλα τα πεδία.")
            return

        update_course(course_id, name, description, category, instructor, start_date, end_date)
        self.update_course_list()#Ανανεωνει τον πίνακα με τα μαθήματα για να εμφανιστούν οι αλλαγές που κάναμε
        self.clear_inputs()#Καθαρίζει τα πεδία κειμένου μετά την ενημέρωση του μαθήματος για να μην μπερδεύει τον Admin αν θέλει να προσθέσει νέο μάθημα ή να ενημερώσει κάποιο άλλο
        #Εφόσον κάνουμε την Ενημέρωση του μαθήματος επαναφέρει το UI στην αρχική του κατάσταση (Reset)
        self.add_course_btn.setText("➕ Προσθήκη Μαθήματος")
        self.add_course_btn.clicked.disconnect()
        self.add_course_btn.clicked.connect(self.add_course)

    def clear_inputs(self):
        for field in [self.name_input, self.description_input, self.category_input, self.instructor_input, self.start_date_input, self.end_date_input]:
            field.clear()

    def open_lectures(self, course_id):
        self.lectures_window = LecturesWindow(course_id, admin=self.admin)
        self.lectures_window.show()

    def open_quiz_selection_dialog(self):        
        dialog = StudentQuizSelectionDialog(self.user_id, self)
        dialog.exec_()

    def open_create_quiz_course_selection(self):
        dialog = AdminQuizCourseSelectionDialog(self) #Ανοίγει ένα παράθυρο για να διαλέξει ο Admin σε ποιο μάθημα θέλει να προσθέσει Quiz
        if dialog.exec_() == QDialog.Accepted: #Αν ο χρήστης πάτησε "ΟΚ" ή "Επιλογή" και δεν έκλεισε απλά το παράθυρο
            selected_course_id = dialog.get_selected_course_id()
            if selected_course_id:#Αν το μαθημα που επελεξε υπάρχει,τότε ανοίγει το παράθυρο δημιουργίας Quiz για αυτό το μάθημα
                self.open_create_quiz_dialog(selected_course_id)

    def open_create_quiz_dialog(self, course_id):
        dialog = QuizDialog(course_id=course_id, parent=self)#Αν έγραφα QuizDialog(course_id, self) θα ήταν το ίδιο ακριβώς, αλλά έτσι είναι πιο ξεκάθαρο
                                                             #parent=self, το νέο παράθυρο να ξέρει ότι "γονέας" του είναι το κεντρικό παράθυρο διαχείρισης,
                                                             #α)δηλαδή λεμε οτι το συγκεκριμένο παραθυρο ανηκει στο κεντρικο παράθυρο με τον πίνακα μαθηματων κλπ. ωστόσο αν ο χρήστης κλείσει το κεντρικό παράθυρο διαχείρισης,
                                                             #  η Qt θα κλείσει και θα διαγράψει αυτόματα από τη μνήμη και όλα τα ανοιχτά Dialogs που έχουν οριστεί ως «παιδιά» του για να μην τρέχουν στο παρασκήνιο.
                                                             #β)Το παράθυρο-παιδί προσπαθεί να εμφανιστεί πάνω και στο κέντρο του γονέα του.
                                                             #γ)Όταν καλείς το dialog.exec_() ο χρήστης δεν μπορεί να κλικάρει πίσω στον πίνακα των μαθημάτων όσο το QuizDialog είναι ανοιχτό
        if dialog.exec_() == QDialog.Accepted:
            new_quiz_id = dialog.created_quiz_id  
            question_dialog = AddMultipleQuestionsDialog(new_quiz_id, parent=self)
            question_dialog.exec_()
        self.update_course_list()

    def go_back(self):
        from main_window import MainWindow
        role = "admin" if self.admin else "student"#Αν η τιμη role είναι admin, τότε το ρόλο που θα περάσουμε στο MainWindow θα είναι "admin", διαφορετικά θα είναι "student"
        self.close()
        self.main_window = MainWindow(role)
        self.main_window.show()

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# --- Παράθυρο Διαλέξεων ---
class LecturesWindow(QWidget):
    def __init__(self, course_id, admin=False):
        super().__init__()
        self.course_id = course_id
        self.admin = admin
        self.setWindowTitle(f"Διαλέξεις Μαθήματος ID {course_id}")
        self.setGeometry(150, 150, 400, 300)

        self.layout = QVBoxLayout()
        self.label = QLabel("Ενέργειες στις διαλέξεις:")
        self.layout.addWidget(self.label)

        self.view_btn = QPushButton("📂 Προβολή Διαλέξεων")
        self.view_btn.clicked.connect(self.view_lectures)
        self.add_btn = QPushButton("➕ Προσθήκη Διάλεξης")
        self.add_btn.clicked.connect(self.add_lecture)

        self.layout.addWidget(self.view_btn)
        self.layout.addWidget(self.add_btn)

        if not self.admin:
            self.add_btn.setDisabled(True)

        self.setLayout(self.layout)

    #ΧΡΕΙΑΖΕΤΑΙ ΑΛΛΑΓΗ ΓΙΑ ΝΑ ΕΙΝΑΙ ΠΙΟ ΦΙΛΙΚΟ ΠΡΟΣ ΤΟΝ ΧΡΗΣΤΗ
    def view_lectures(self):
        folder_path = os.path.join("lectures", f"course_{self.course_id}")
        if os.path.exists(folder_path):
            if os.name == 'nt':
                os.startfile(folder_path)
            else:
                subprocess.run(["xdg-open", folder_path])
        else:
            QMessageBox.information(self, "Πληροφορία", "Δεν υπάρχουν διαλέξεις.")

    #ΧΡΕΙΑΖΕΤΑΙ ΑΛΛΑΓΗ ΓΙΑ ΝΑ ΕΙΝΑΙ ΠΙΟ ΦΙΛΙΚΟ ΠΡΟΣ ΤΟΝ ΧΡΗΣΤΗ
    def add_lecture(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Επιλέξτε αρχείο")
        if file_path:
            folder_path = os.path.join("lectures", f"course_{self.course_id}")
            os.makedirs(folder_path, exist_ok=True)
            target_path = os.path.join(folder_path, os.path.basename(file_path))
            try:
                import shutil
                shutil.copy(file_path, target_path)
                QMessageBox.information(self, "Επιτυχία", "Η διάλεξη προστέθηκε.")
            except Exception as e:
                QMessageBox.warning(self, "Σφάλμα", f"Αποτυχία: {e}")

# --- Διάλογοι Quiz & Εγγραφής ---
class QuizDialog(QDialog):
    def __init__(self, course_id, parent=None):
        super().__init__(parent)
        self.course_id = course_id
        self.setWindowTitle("Δημιουργία Quiz")
        self.setGeometry(100, 100, 400, 300)
        self.layout = QVBoxLayout()

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Τίτλος Quiz")
        self.layout.addWidget(self.title_input)

        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Περιγραφή Quiz")
        self.layout.addWidget(self.description_input)

        self.create_btn = QPushButton("➕ Προσθήκη Ερωτήσεων")
        self.create_btn.clicked.connect(self.create_quiz_and_add_questions)
        self.layout.addWidget(self.create_btn)
        self.setLayout(self.layout)

    def create_quiz_and_add_questions(self):
        title = self.title_input.text().strip()
        desc = self.description_input.text().strip()
        if not title or not desc:
            QMessageBox.warning(self, "Προειδοποίηση", "Συμπλήρωσε τα πεδία.")
            return
        try:
            conn = sqlite3.connect("lms.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO quizzes (course_id, title, description) VALUES (?, ?, ?)", (self.course_id, title, desc))
            conn.commit()
            self.created_quiz_id = cursor.lastrowid
            conn.close()
            self.accept()
        except Exception as e: #Εμφανίζει ένα κόκκινο εικονίδιο με "X" (το σύμβολο του κρίσιμου σφάλματος).Σταματάει τη ροή του προγράμματος μέχρι ο χρήστης να πατήσει "OK"
            QMessageBox.critical(self, "Σφάλμα", str(e))

class AddMultipleQuestionsDialog(QDialog):
    def __init__(self, quiz_id, total_questions=5, parent=None):
        super().__init__(parent)
        self.quiz_id = quiz_id
        self.total_questions = total_questions
        self.current_question = 1

        self.setWindowTitle("Προσθήκη Ερωτήσεων")
        self.setGeometry(100, 100, 400, 450)
        self.layout = QVBoxLayout()

        self.title = QLabel(f"Ερώτηση {self.current_question} από {self.total_questions}")
        self.layout.addWidget(self.title)

        self.question_input = QLineEdit()
        self.question_input.setPlaceholderText("Ερώτηση")
        self.layout.addWidget(self.question_input)

        self.option_a = QLineEdit(); self.option_a.setPlaceholderText("Επιλογή A")
        self.option_b = QLineEdit(); self.option_b.setPlaceholderText("Επιλογή B")
        self.option_c = QLineEdit(); self.option_c.setPlaceholderText("Επιλογή C")
        self.option_d = QLineEdit(); self.option_d.setPlaceholderText("Επιλογή D")
        self.correct_option = QLineEdit(); self.correct_option.setPlaceholderText("Σωστή (A, B, C, D)")

        for w in [self.option_a, self.option_b, self.option_c, self.option_d, self.correct_option]:
            self.layout.addWidget(w) #Δημιουργεί μια προσωρινή ομάδα που περιέχει τα κουμπιά ή τα πεδία κειμένου των επιλογών (A, B, C, D) και της σωστής απάντησης

        self.submit_btn = QPushButton("Υποβολή Ερώτησης")
        self.submit_btn.clicked.connect(self.submit_question)
        self.layout.addWidget(self.submit_btn)
        self.setLayout(self.layout)

    #ΕΛΕΓΧΟΣ ΟΤΙ ΟΙ ΕΠΙΛΟΓΕΣ ΕΧΟΥΝ ΣΥΜΠΛΗΡΩΘΕΙ ΚΑΙ ΟΤΙ Η ΣΩΣΤΗ ΑΠΑΝΤΗΣΗ ΕΙΝΑΙ ΜΙΑ ΑΠΟ ΤΙΣ 4 ΕΠΙΛΟΓΕΣ, ΠΡΙΝ ΠΡΟΣΠΑΘΗΣΕΙ ΝΑ ΤΗΝ ΠΡΟΣΘΕΣΕΙ ΣΤΗ ΒΑΣΗ ΔΕΔΟΜΕΝΩΝ. ΑΝ Ο ΕΛΕΓΧΟΣ ΑΠΟΤΥΧΕΙ, ΕΜΦΑΝΙΖΕΤΑΙ ΕΝΑ ΜΗΝΥΜΑ ΠΡΟΕΙΔΟΠΟΙΗΣΗΣ ΚΑΙ Η ΕΡΩΤΗΣΗ ΔΕΝ ΠΡΟΣΤΕΘΗΚΕ.
    def submit_question(self):
        q = self.question_input.text().strip()
        ans = [self.option_a.text(), self.option_b.text(), self.option_c.text(), self.option_d.text()]
        correct = self.correct_option.text().strip().upper()

        if not q or not all(ans) or correct not in ['A', 'B', 'C', 'D']:
            QMessageBox.warning(self, "Σφάλμα", "Συμπληρώστε σωστά τα πεδία.")
            return

        success = add_question_to_quiz(self.quiz_id, q, *ans, correct)
        if success:
            if self.current_question < self.total_questions: #Εμφανίζει τον αριθμο της τρέχουσας ερωτησης που φτιαχνουμε και το αυξανει καθε φορα σύμφωνα με τον συνολικό αριθμό ερωτήσεων(π.χ.Ερωτηση 2 από 4)
                self.current_question += 1
                self.title.setText(f"Ερώτηση {self.current_question} από {self.total_questions}")
                for w in [self.question_input, self.option_a, self.option_b, self.option_c, self.option_d, self.correct_option]:
                    w.clear()  #Θεωρητικά w= ενα widget από τα πεδία ερωτήσεων και επιλογών, οπότε με το w.clear() καθαρίζουμε όλα τα πεδία για να γράψουμε την επόμενη ερώτηση
            else:
                QMessageBox.information(self, "Τέλος", "Όλες οι ερωτήσεις προστέθηκαν.")
                self.accept()

