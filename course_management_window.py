import sqlite3
from styles_css import styles
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QLabel, QDialog, QMessageBox, QLabel, QDialog, QHeaderView, QStackedWidget, QGraphicsScene, QGraphicsPixmapItem, QGraphicsBlurEffect
from PyQt5.QtCore import Qt, QSize, QPropertyAnimation, QEvent, QRectF, QEasingCurve
from PyQt5.QtGui import QPixmap, QPainter, QIcon, QCursor, QImage, QColor, QBrush
from db import get_enrolled_courses, add_question_to_quiz, create_course,update_course, get_all_courses, delete_course, unenroll_user_from_course, get_user_by_id, get_student_quiz_leaderboard
from student_functions.student_quiz_selection_dialog import StudentQuizSelectionDialog
from student_functions.student_quiz_stats_page import StudentQuizStatsPage
from quiz_functions.quiz_selectiondialog import AdminQuizCourseSelectionDialog
from subjects_interface.subjects_available_interface import EnrollPage
import qtawesome as qta
from lectures_functions.lectures_functions import LecturesPage


class TableWithBackground(QTableWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bg_pixmap = QPixmap('icons/e-learning.png')
        self.scaled_pixmap = QPixmap()
        self.blur_radius = 8 #Βαθμός του blur, όσο μεγαλύτερος είναι ο αριθμός, τόσο πιο θολή θα είναι η εικόνα.
        self.verticalHeader().setVisible(False)  # Κρύβουμε τους αριθμούς αριστερά

    def _blur_pixmap(self, pixmap):
        """Χρησιμοποιώ το pipeline της Qt (QGraphicsScene + QGraphicsBlurEffect) για να πάρει ένα pixmap
           και να μου γυρίσει τη θολωμένη version του, που μετά τη χρησιμοποιώ ως background """
        if pixmap.isNull() or self.blur_radius <= 0:
            return pixmap

        scene = QGraphicsScene()
        item = QGraphicsPixmapItem(pixmap)
        blur_effect = QGraphicsBlurEffect()
        blur_effect.setBlurRadius(self.blur_radius)#Ορίζει πόσο έντονο θα είναι το blur (όσο μεγαλύτερο, τόσο πιο θολό)
        item.setGraphicsEffect(blur_effect)
        scene.addItem(item)

        result = QImage(pixmap.size(), QImage.Format_ARGB32_Premultiplied)#Δημιουργεί “καμβά” εξόδου (QImage) ίδιου μεγέθους με alpha κανάλι (διαφάνεια)
        result.fill(Qt.transparent) #Το result είναι μια νέα εικόνα (QImage) που τη φτιάχνω για να ζωγραφίσω μέσα της το blur αποτέλεσμα.
                                     #Μετά το scene.render ζωγραφίζει πάνω σε αυτήν την καθαρή διαφανή βάση μόνο το θολωμένο pixmap.
        painter = QPainter(result)
        scene.render(painter, QRectF(result.rect()), QRectF(0, 0, pixmap.width(), pixmap.height()))#Κάνει render τη σκηνή (άρα την εικόνα με blur) πάνω στο result
        painter.end()

        return QPixmap.fromImage(result)#Μετατρέπει το τελικό QImage πίσω σε QPixmap και το επιστρέφει για να το χρησιμοποιήσουμε ως background.

    # Όταν αλλάζει το μέγεθος του πίνακα, ανανεώνουμε την κλίμακα της εικόνας background για να καλύπτει όλο το πίνακα
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if not self.bg_pixmap.isNull():
            w = self.viewport().width()
            h = self.viewport().height()
            scaled = self.bg_pixmap.scaled(w, h, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            self.scaled_pixmap = self._blur_pixmap(scaled)
        self.viewport().update()

    def paintEvent(self, event):  # Τοποθετώ την εικόνα background πίσω από τα δεδομένα του πίνακα
        painter = QPainter(self.viewport())
        # Ελέγχει αν υπάρχει η εικόνα και αν έχει ήδη κλιμακωθεί σωστά στο μέγεθος του παραθύρου
        if hasattr(self, 'scaled_pixmap') and self.scaled_pixmap:
            # ΚΕΝΤΡΑΡΙΣΜΑ ΕΙΚΟΝΑΣ
            x = (self.viewport().width() - self.scaled_pixmap.width()) // 2
            # ΚΕΝΤΡΑΡΙΣΜΑ ΕΙΚΟΝΑΣ
            y = (self.viewport().height() - self.scaled_pixmap.height()) // 2
            painter.drawPixmap(x, y, self.scaled_pixmap)
        super().paintEvent(event)


class CourseManagementWindow(QWidget):
    def __init__(self, user_id, admin=False):
        super().__init__()
        self.user_id = user_id
        self.admin = admin
        self.setWindowTitle("Διαχείριση Μαθημάτων")
        self.setGeometry(100, 100, 1200, 820)
        self.setStyleSheet(styles.get_main_window_style())

        self.init_ui()

    def init_ui(self):
        self.outer_layout = QVBoxLayout(self)
        self.outer_layout.setContentsMargins(0, 0, 0, 0)
        self.outer_layout.setSpacing(0)

        # Ενεργοποίηση στο κεντρικό παράθυρο,του hover για το menu_btn
        self.setMouseTracking(True)
        # Προσθήκη αυτού για να παρακολουθεί όλο το παράθυρο
        self.installEventFilter(self)

        # TOP BAR - Το κουμπί μένει εδώ για να μην χάνεται ποτέ
        self.top_bar = QFrame()
        # Για να μπορεί να παρακολουθεί το ποντίκι και να στείλει το event για να ανοιξει το μενου αν είναι κλειστό
        self.top_bar.setMouseTracking(True)
        self.top_bar.setFixedHeight(50)
        self.top_bar.setStyleSheet(
            "background-color: #34405e; border-bottom: 1px solid #2c3e50;")
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
        # Για να καλυπτει όλη την επιφάνεια,να είναι κολλημένο και με το content
        self.sidebar_vbox.setContentsMargins(0, 0, 0, 0)
        self.sidebar_vbox.setSpacing(0)

        # 1. ΣΤΑΘΕΡΟ HEADER (Icon + Title) - Αυτό δεν κλείνει ποτέ - Κεντραρισμένο
        self.sidebar_header = QFrame()
        self.sidebar_header.setFixedHeight(70)
        self.sidebar_header.setStyleSheet("background-color: #1a252f; border-bottom: 1px solid #34495e;")

        # Χρησιμοποιούμε κάθετο layout για να μπει ο τίτλος ΚΑΤΩ από το κουμπί
        header_layout = QVBoxLayout(self.sidebar_header)

        # Δημιουργία οριζόντιου layout ΜΟΝΟ για το κουμπί ώστε να κεντραριστεί οριζόντια
        btn_container = QHBoxLayout()
        btn_container.addStretch()  # Σπρώχνει από αριστερά

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

        # Το "1" αναγκάζει το body να πιάσει όλο το ύψος
        self.sidebar_vbox.addWidget(self.sidebar_body, 1)

        # --- CONTENT AREA (Δεξί Panel) ---
        self.content_stack = QStackedWidget()
        self.create_profile_page()      # Σελίδα 0: Προφίλ
        self.create_course_list_page()  # Σελίδα 1: Λίστα Μαθημάτων

        # Index 2: Admin Tools (Αν είναι student, βάζουμε ένα κενό widget για να κρατήσουμε τη θέση)
        if self.admin:
            self.create_admin_tools_page()
        else:
            empty_widget = QWidget()
            self.content_stack.addWidget(empty_widget)  # Κρατάει το Index 2

        if not self.admin:  # Σελίδα 3: Εγγραφή (για Student)
            self.enroll_page = EnrollPage(self.user_id, self)
            # Αυτό θα είναι τώρα το Index 3
            self.content_stack.addWidget(self.enroll_page)
        else:  # Αν είναι admin, βάζω πάλι ένα κενό widget για να μην μπερδευτούν τα index αν προστεθεί κάτι μετά
            self.content_stack.addWidget(QWidget())

        # Σελίδα 4: Στατιστικά (Για όλους ή μονο για student)
        self.stats_page = StudentQuizStatsPage(self.user_id, self)
        self.content_stack.addWidget(self.stats_page)

        # Σύνθεση κύριου layout
        self.main_content_layout.addWidget(self.sidebar_container)
        self.main_content_layout.addWidget(self.content_stack, 1)

        self.outer_layout.addLayout(self.main_content_layout)

        # Εφαρμόζουμε το event_filter για να ακούει οτι υπάρχει στο top_bar,content_stack για να συμβάλει στο auto-close-menu
        self.apply_filter_to_children(self.content_stack)
        self.apply_filter_to_children(self.top_bar)

    # Συνάρτηση για να ακούει το event filter οτιδηποτε πατησουμε στο content-area και να γινει το auto-close-menu
    def apply_filter_to_children(self, widget):
        # Εγκαθιστά τον filter στο ίδιο το widget
        widget.installEventFilter(self)
        # Και επαναληπτικά σε όλα τα παιδιά του (κουμπιά, inputs, κλπ)
        for child in widget.findChildren(QWidget):
            child.installEventFilter(self)

    def showEvent(self, event):
        super().showEvent(event)

        # Αρχικά κλειστό sidebar
        self.sidebar_visible = False
        # Σε κλειστή κατάσταση αφήνουμε μόνο τα icons ορατά.
        self.sidebar_header.hide()
        self.sidebar_body.show()
        self.set_sidebar_expanded(False)#Το sidebar_expanded είναι Icons + Γράμματα
        self.sidebar_container.setMinimumWidth(70)
        self.sidebar_container.setMaximumWidth(70)

    def eventFilter(self, obj, event):
        """Auto-open & Auto-close Menu,όταν γίνεται hover στο menu icon και στα menu buttons"""
        
        # Όταν το ποντίκι μπει πάνω στο menu button ή στα icons του sidebar auto-open-menu
        sidebar_hover_targets = []
        for attr_name in ["menu_btn", "btn_profile", "btn_courses", "btn_stats", "back_btn", "btn_admin", "btn_enroll"]:
            target = getattr(self, attr_name, None)
            if target is not None:
                sidebar_hover_targets.append(target)
        
        #Mόλις το ποντίκι μπει πάνω σε συγκεκριμένα κουμπιά του menu, αν το sidebar είναι κλειστό, ανοίγει.
                                                                         #Το widget πάνω στο οποίο μπήκε (obj) είναι ένα από τα επιτρεπτά targets της λίστας sidebar_hover_targets (π.χ. menu button ή sidebar icons).
        if event.type() == QEvent.Enter and obj in sidebar_hover_targets:#Το event είναι Enter (δηλαδή ο δείκτης του ποντικιού μόλις μπήκε πάνω σε widget).
            if not self.sidebar_visible:#Κρατά ανοιχτό το sidebar και μετά το auto-open με το hover          
                self.toggle_sidebar()
            return False

        # Auto-Close: MouseButtonPress σε οποιοδήποτε αντικείμενο ΕΚΤΟΣ sidebar
        if event.type() == QEvent.MouseButtonPress:
            if self.sidebar_visible:
                # Μετατρέπουμε τη θέση του κλικ σε global και μετά σε τοπική,ως προς το CourseManagementWindow (self)
                click_pos = self.mapFromGlobal(QCursor.pos())

                if click_pos.x() > self.sidebar_container.width():  # Αν το κλικ έγινε δεξιά από το όριο του sidebar
                    self.toggle_sidebar()
                    return False  # Επιστρέφουμε False για να εκτελεστεί κανονικά το κλικ στο κουμπί ή στο input που πατήθηκε

        return super().eventFilter(obj, event)

    def toggle_sidebar(self):
        if hasattr(self, 'animation') and self.animation.state() == QPropertyAnimation.Running:
            return  # Αν ήδη τρέχει το animation τότε προχώρα

        current_width = self.sidebar_container.width()

        if current_width == 70:
            end_width = 250
            self.sidebar_visible = True
            self.sidebar_container.setMaximumWidth(250)
        else:
            end_width = 70
            self.sidebar_visible = False
            self.sidebar_header.hide()
            self.sidebar_body.show()
            self.sidebar_container.setMaximumWidth(70)
            self.set_sidebar_expanded(False)

        self.animation = QPropertyAnimation(self.sidebar_container, b"minimumWidth")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.InOutCubic)
        self.animation.setStartValue(current_width)
        self.animation.setEndValue(end_width)
        self.animation.finished.connect(self.on_animation_finished)#Εμφανίζει τα γράμματα δίπλα από τα icons ,στο menu sidebar,μόλις τελειώσει το animation του ανοίγματος,για να μην εμφανίζονται τα γράμματα πριν ολοκληρωθεί το άνοιγμα του menu
        self.animation.start()

    def on_animation_finished(self):
        """Η συνάρτηση αυτή εκτελείται όταν τελειώνει το animation του sidebar και «ολοκληρώνει» το οπτικό άνοιγμα του menu."""
        if self.sidebar_visible:
            self.sidebar_header.show()#Εμφανίζει το header του sidebar (το πάνω κομμάτι με τίτλο/menu area).
            self.sidebar_body.show()#Εμφανίζει το body του sidebar (τα κουμπιά επιλογών).
            self.set_sidebar_expanded(True)#Expanded Mode = δείχνει κείμενο δίπλα στα icons,μεγαλώνει πλάτη/μορφοποίηση κουμπιών για «ανοιχτό» menu.
            self.sidebar_title_label.show()
            self.sidebar_header.setStyleSheet("background-color: #1a252f; border-bottom: 1px solid #34495e;") #Εφαρμόζω ξανά το style του header (χρώμα φόντου + border), ώστε η τελική εμφάνιση να είναι σωστή/σταθερή μετά το animation.

    def set_sidebar_expanded(self, expanded):
        """ expanded=True: icon + κείμενο, expanded=False: μόνο icon. """
        button_width = 250 if expanded else 40
        self.sidebar_body_layout.setContentsMargins(15, 5, 5, 15) if expanded else self.sidebar_body_layout.setContentsMargins(10, 5, 10, 15)

        buttons_with_text = [#Τα κουμπιά που υπάρχουν σε όλους τους χρήστες,τα βάζω πάντα στη λίστα για να αλλάζει το κείμενο τους ανάλογα με το αν είναι expanded ή όχι
            (self.btn_profile, " Προφίλ"),
            (self.btn_courses, " Μαθήματα"),
            (self.btn_stats, " Στατιστικά"),
            (self.back_btn, "Αποσύνδεση"),
        ]

        if self.admin and hasattr(self, 'btn_admin'):
            buttons_with_text.insert(2, (self.btn_admin, " Διαχείριση Quiz"))
        if not self.admin and hasattr(self, 'btn_enroll'):
            buttons_with_text.insert(2, (self.btn_enroll, " Εγγραφή"))

        for button, text in buttons_with_text:
            button.setText(text if expanded else "")
            button.setFixedWidth(button_width)
            button.setCursor(Qt.PointingHandCursor if expanded else Qt.ArrowCursor)

    def setup_sidebar_buttons_to_layout(self, sidebar_body_layout):
        """Βοηθητική συνάρτηση για να τοποθετήσουμε τα κουμπιά στο νέο layout"""
        self.btn_profile = QPushButton(" Προφίλ")
        self.btn_profile.setIcon(QIcon("icons/name-icon.png"))
        self.btn_profile.setIconSize(QSize(15, 15))
        self.btn_profile.setFixedSize(40, 40)
        self.btn_profile.setFixedWidth(250)
        self.btn_profile.clicked.connect(
            lambda: self.content_stack.setCurrentIndex(0))
        sidebar_body_layout.addWidget(self.btn_profile)

        self.btn_courses = QPushButton(" Μαθήματα")
        self.btn_courses.setIcon(QIcon("icons/education.png"))
        self.btn_courses.setIconSize(QSize(15, 15))
        self.btn_courses.setFixedSize(40, 40)
        self.btn_courses.setFixedWidth(250)
        self.btn_courses.clicked.connect(
            lambda: self.content_stack.setCurrentIndex(1))
        sidebar_body_layout.addWidget(self.btn_courses)

        if self.admin:
            self.btn_admin = QPushButton(" Διαχείριση Quiz")
            self.btn_admin.setIcon(QIcon("icons/online-test.png"))
            self.btn_admin.setIconSize(QSize(15, 15))
            self.btn_admin.setFixedSize(40, 40)
            self.btn_admin.setFixedWidth(250)
            self.btn_admin.clicked.connect(
                lambda: self.content_stack.setCurrentIndex(2))
            self.sidebar_body_layout.addWidget(self.btn_admin)
        else:
            self.btn_enroll = QPushButton(" Εγγραφή")
            self.btn_enroll.setIcon(QIcon("icons/edit.png"))
            self.btn_enroll.setIconSize(QSize(15, 15))
            self.btn_enroll.setFixedSize(40, 40)
            self.btn_enroll.setFixedWidth(250)
            self.btn_enroll.clicked.connect(
                lambda: self.content_stack.setCurrentIndex(3))
            self.sidebar_body_layout.addWidget(self.btn_enroll)

        self.btn_stats = QPushButton(" Στατιστικά")
        self.btn_stats.setIcon(QIcon("icons/stats.png"))
        self.btn_stats.setIconSize(QSize(15, 15))
        self.btn_stats.setFixedSize(40, 40)
        self.btn_stats.setFixedWidth(250)
        self.btn_stats.clicked.connect(
            lambda: self.content_stack.setCurrentIndex(4))
        self.sidebar_body_layout.addWidget(self.btn_stats)

        # Αυτό το stretch σπρώχνει ό,τι ακολουθεί στο κάτω μέρος του sidebar
        self.sidebar_body_layout.addStretch(1)
        self.apply_filter_to_children(sidebar_body_layout)

        back_btn_layout = QHBoxLayout()
        # Το stretch στην αρχή του οριζόντιου layout σπρώχνει το κουμπί δεξιά
        back_btn_layout.addStretch(1)

        self.back_btn = QPushButton("Αποσύνδεση")
        self.back_btn.setIcon(QIcon("icons/sign-out.png"))
        self.back_btn.setIconSize(QSize(15, 15))
        self.back_btn.setFixedSize(40, 40)
        self.back_btn.setFixedWidth(250)
        self.back_btn.clicked.connect(self.go_back)

        back_btn_layout.addWidget(self.back_btn)
        back_btn_layout.addStretch(1)
        self.apply_filter_to_children(back_btn_layout)

        self.sidebar_body_layout.addLayout(back_btn_layout)

        # Εφαρμογή event filter στα κουμπιά του menu ώστε το hover πάνω στα icons να ανοίγει το sidebar.
        sidebar_buttons = [self.btn_profile, self.btn_courses, self.btn_stats, self.back_btn]
        if self.admin and hasattr(self, 'btn_admin'):
            sidebar_buttons.append(self.btn_admin)
        if not self.admin and hasattr(self, 'btn_enroll'):
            sidebar_buttons.append(self.btn_enroll)

        for btn in sidebar_buttons:#Εγκαθιστά το event filter σε όλα τα κουμπιά του sidebar για να ακούει το hover και να ανοίγει το menu
            btn.installEventFilter(self)

    def create_profile_page(self):
        """Σελίδα 0: Προφίλ Χρήστη (Κοινή για Admin και Student)"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(16)

        card = QFrame()
        card.setStyleSheet("background: white; border-radius: 10px; padding: 8px;")
        card.setMaximumHeight(260)#Ύψος του frame που έχει τα στοιχεία φοιτητή(Ονοματεπώνυμο,email κλπ)
        card_layout = QVBoxLayout(card)

        user = get_user_by_id(self.user_id)#Καλώ αυτη την συνάρτηση από το db.py για να πάρω τα στοιχεία του χρήστη που είναι αποθηκευμένα στη βάση δεδομένων

        if user:#Αν ο χρήστης βρέθηκε στη βάση δεδομένων.
            _, username, email, role = user # κάνει unpack του tuple,αγνοεί το πρώτο πεδίο με _,βάζει τα επόμενα σε username, email, role
        else:
            username = "-"
            email = "-"
            role = "admin" if self.admin else "student"

        welcome_row = QHBoxLayout()
        welcome_icon = QLabel()

        custom_welcome_pixmap = QPixmap("icons/welcome_icon.png")
        welcome_icon.setPixmap(custom_welcome_pixmap.scaled(30, 30, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        welcome_icon.setFixedSize(30, 30)
        welcome_icon.setAlignment(Qt.AlignVCenter)
        
        title = QLabel(f"Καλώς Ήρθες, {username}!")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 10px; color: #2c3e50;")
        welcome_row.addSpacing(11)#Προσθέτω κενό πριν το welcome_icon
        welcome_row.addWidget(welcome_icon)
        welcome_row.addWidget(title)
        welcome_row.addStretch()
        layout.addLayout(welcome_row)
 
        # Σειρά 1: Όνομα χρήστη
        username_row = QHBoxLayout()
        username_label_text = QLabel("Όνομα χρήστη:")
        username_label_text.setStyleSheet("font-size: 16px; color: #2c3e50; font-weight: bold;")
        username_label_value = QLabel(username)
        username_label_value.setStyleSheet("font-size: 16px; color: #2c3e50;")
        username_row.addWidget(username_label_text)
        username_row.addWidget(username_label_value)
        card_layout.addLayout(username_row)

        # Σειρά 2: Email
        email_row = QHBoxLayout()
        email_label_text = QLabel("Email:")
        email_label_text.setStyleSheet("font-size: 16px; color: #2c3e50; font-weight: bold;")
        email_label_value = QLabel(email)
        email_label_value.setStyleSheet("font-size: 16px; color: #2c3e50;")
        email_row.addWidget(email_label_text)
        email_row.addWidget(email_label_value)
        card_layout.addLayout(email_row)

        # Σειρά 3: Ρόλος
        role_row = QHBoxLayout()
        role_label_text = QLabel("Ρόλος:")
        role_label_text.setStyleSheet("font-size: 16px; color: #2c3e50; font-weight: bold;")
        role_label_value = QLabel(role)
        role_label_value.setStyleSheet("font-size: 16px; color: #2c3e50;")
        role_row.addWidget(role_label_text)
        role_row.addWidget(role_label_value)
        card_layout.addLayout(role_row)

        # Σειρά 4: ID χρήστη
        id_row = QHBoxLayout()
        id_label_text = QLabel("ID χρήστη:")
        id_label_text.setStyleSheet("font-size: 16px; color: #2c3e50; font-weight: bold;")
        id_label_value = QLabel(str(self.user_id))
        id_label_value.setStyleSheet("font-size: 16px; color: #2c3e50;")
        id_row.addWidget(id_label_text)
        id_row.addWidget(id_label_value)
        card_layout.addLayout(id_row)

        layout.addWidget(card)

        if not self.admin:
            """Card που εμφανίζει το leaderboard των quiz που έχουν κάνει φοιτητές"""
            leaderboard_card = QFrame()
            leaderboard_card.setStyleSheet("background: white; border-radius: 10px; padding: 20px;")
            leaderboard_card.setMinimumHeight(420)#Υψος του card που περιέχει το leaderboard
            leaderboard_layout = QVBoxLayout(leaderboard_card)

            leaderboard_title = QLabel("Leaderboard Quiz")
            leaderboard_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50; margin-bottom: 8px;")
            leaderboard_layout.addWidget(leaderboard_title)

            rows = get_student_quiz_leaderboard(self.user_id)
            if not rows:
                empty_label = QLabel("Δεν υπάρχουν ακόμα αποτελέσματα quiz.")
                empty_label.setStyleSheet("font-size: 16px; color: #5f6d7a;")
                leaderboard_layout.addWidget(empty_label)
            else:
                leaderboard_table = QTableWidget()
                leaderboard_table.setColumnCount(4)
                leaderboard_table.setHorizontalHeaderLabels(["Μάθημα", "Quiz", "Ημερομηνία", "Βαθμός (%)"])
                leaderboard_table.setRowCount(len(rows))
                leaderboard_table.verticalHeader().setVisible(False)
                leaderboard_table.setEditTriggers(QTableWidget.NoEditTriggers)
                leaderboard_table.setSelectionMode(QTableWidget.NoSelection)
                leaderboard_table.setFocusPolicy(Qt.NoFocus)
                leaderboard_table.setAlternatingRowColors(True)
                leaderboard_table.setWordWrap(False)
                leaderboard_table.setStyleSheet(styles.leaderboard_student_style())

                leaderboard_header = leaderboard_table.horizontalHeader()
                leaderboard_header.setVisible(True)
                leaderboard_header.setDefaultAlignment(Qt.AlignCenter)
                leaderboard_header.setStretchLastSection(True)

                rows_header = leaderboard_table.verticalHeader()
                rows_header.setSectionResizeMode(QHeaderView.Fixed)
                rows_header.setDefaultSectionSize(34)
                

                for col in range(leaderboard_table.columnCount()):
                    header_item = leaderboard_table.horizontalHeaderItem(col)
                    if header_item:
                        header_item.setTextAlignment(Qt.AlignCenter)
                        header_item.setForeground(QBrush(QColor("#1f2d3a")))
                        header_font = header_item.font()
                        header_font.setBold(True)
                        header_item.setFont(header_font)

                for row_idx, row_data in enumerate(rows):
                    course_name, quiz_title, date_taken, score = row_data
                    values = [course_name, quiz_title, date_taken, f"{float(score):.2f}"]
                    for col_idx, value in enumerate(values):
                        item = QTableWidgetItem(str(value))
                        item.setTextAlignment(Qt.AlignCenter)
                        leaderboard_table.setItem(row_idx, col_idx, item)

                # Όλες οι στήλες κάνουν stretch για να γεμίζει πλήρως το πλάτος του πίνακα
                header = leaderboard_table.horizontalHeader()

                # Οι 3 στήλες stretch
                for i in range(3):
                    header.setSectionResizeMode(i, QHeaderView.Stretch)

                leaderboard_table.setMinimumHeight(420)#Υψος του πινακα
                leaderboard_layout.addWidget(leaderboard_table)

            layout.addWidget(leaderboard_card)


        layout.addStretch()
        self.content_stack.addWidget(page)

    def create_course_list_page(self):
        """Σελίδα 1: Λίστα Μαθημάτων (Κοινή για Admin και Student)"""
        page = QWidget()
        layout = QVBoxLayout(page)

        title = QLabel(
            "Τα μαθήματα μου" if not self.admin else "Πίνακας Ελέγχου Μαθημάτων")
        title.setStyleSheet(
            "font-size: 24px; font-weight: bold; margin: 10px; color: #2c3e50;")
        layout.addWidget(title)

        self.table = TableWithBackground()
        self.table.setColumnCount(7)
        self.table_title_color = "#FFFFFF" if not self.admin else "#2c3e50"
        self.table.setStyleSheet(
            f"QTableWidget {{ color: {self.table_title_color}; font-family: 'Noto Sans', 'Segoe UI', Arial, sans-serif; font-size: 17px; font-weight: 600; }}")
        self.table.setHorizontalHeaderLabels(
            ["Όνομα", "Περιγραφή", "Κατηγορία", "Εκπαιδευτής", "Έναρξη", "Λήξη", "Ενέργειες"])

        # Ορίζω τη στήλη 6("Ενέργειες") ως Fixed και δίνω το πλάτος της,120,για να την μικρήνω και να την κάνω να χωράει τα κουμπιά, Διαλέξεις και απεγγραφή
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Fixed)
        self.table.setColumnWidth(6, 120)

        # Όλες οι στήλες εκτός της τελευταίας κάνουν stretch
        for i in range(6):
            self.table.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)

        # Όταν ο χρήστης κάνει κλικ σε ένα κελί του πίνακα, καλείται η μέθοδος on_table_item_clicked που θα χειρίζεται την εμφάνιση των πληροφοριών του μαθήματος στα πεδία κειμένου για τον Admin ή θα ανοίγει τις διαλέξεις για τον Student
        self.table.cellClicked.connect(self.on_table_item_clicked)
        layout.addWidget(self.table)

        # Προσθέτουμε αυτή τη σελίδα στη στοίβα του content_stack, ώστε να μπορεί να εμφανιστεί όταν πατηθεί το κουμπί "Μαθήματα" στο sidebar
        self.content_stack.addWidget(page)
        self.update_course_list()  # Φορτώνουμε τα μαθήματα από τη βάση δεδομένων και τα εμφανίζουμε στον πίνακα κάθε φορά που δημιουργείται αυτή η σελίδα, ώστε να είναι πάντα ενημερωμένη με τις τελευταίες αλλαγές (π.χ. νέες εγγραφές, προσθήκη/διαγραφή μαθημάτων από τον Admin)

    def create_admin_tools_page(self):
        """Σελίδα 2: Φόρμα Διαχείρισης μόνο για Admin"""
        page = QWidget()
        layout = QVBoxLayout(page)

        title = QLabel("Επεξεργασία Μαθημάτων & Διαχείριση Quiz")
        title.setStyleSheet(
            "font-size: 20px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)

        # Φτιάχνω ένα container-πλαίσιο για να βάλω τα πεδία κειμένου("όνομα,περιγραφή κλπ.")
        form_container = QFrame()
        form_container.setStyleSheet(
            "background: white; border-radius: 10px; padding: 20px;")
        # Τοποθετώ τα πεδία κειμένου μέσα στο form_container για να έχουν λευκό φόντο και να ξεχωρίζουν από το υπόλοιπο περιεχόμενο της σελίδας
        form_layout = QVBoxLayout(form_container)

        # Πεδία Εισαγωγής για τα στοιχεία του μαθήματος που θέλει να προσθέσει ή να ενημερώσει ο Admin
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

        # Buttons Λειτουργιών
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
        # Όταν ο Admin κάνει κλικ στον πίνακα, τον μεταφέρουμε αυτόματα στη σελίδα επεξεργασίας(CurrentIndex(2))
        if self.admin:
            self.content_stack.setCurrentIndex(2)

            # Στήλη 0: Περιέχει το Όνομα και το Κρυφό ID (UserRole)
            item_name = self.table.item(row, 0)
            # Παίρνουμε το σωστό ID για το update
            course_id = item_name.data(Qt.UserRole)

            self.name_input.setText(item_name.text())
            self.description_input.setText(self.table.item(row, 1).text())
            self.category_input.setText(self.table.item(row, 2).text())
            self.instructor_input.setText(self.table.item(row, 3).text())
            self.start_date_input.setText(self.table.item(row, 4).text())
            self.end_date_input.setText(self.table.item(row, 5).text())

            self.add_course_btn.setText("📝 Ενημέρωση Μαθήματος")

            try:
                # Αποεπιλεγουμε το μαθημα που ειχαμε επιλεξει να αλλαξουμε-ενημέρωση
                self.add_course_btn.clicked.disconnect()
            except:
                pass  # "Αν δεν έχουμε τίποτα να αποσυνδέσουμε, εντάξει, απλά προχωράμε"

            # lambda = "Όταν σε πατήσουν, κάλεσε τη συνάρτηση update_course για το συγκεκριμένο ID μαθήματος που μόλις κάναμε κλικ στον πίνακα"
            self.add_course_btn.clicked.connect(
                lambda: self.update_course(course_id))

    def update_course_list(self):
        if self.admin:
            courses = get_all_courses()
        else:
            courses = get_enrolled_courses(self.user_id)

        # Σταθερά χρώματα ανά κελί ώστε να διαβάζονται πάντα τα γράμματα πάνω στο background.
        if self.admin:#Στον admin έχω βάλει μπεζ αποχρώσεις σαν background στα κελιά,ανοιχτό μπεζ και πιο σκουρο μπεζ-εναλλάξ
            cell_bg_even = QColor(255, 248, 232, 235)
            cell_bg_odd = QColor(246, 236, 214, 235)
            cell_text_color = QColor("#2c3e50")#2c3e50 για να ξεχωρίζουν τα γράμματα πάνω στο ανοιχτό background
        else: #Στον student έχω βάλει σκούρες αποχρώσεις σαν background στα κελιά,σκούρο μπλε-γκρι και πιο σκούρο μπλε-γκρι-εναλλάξ
            cell_bg_even = QColor(12, 10, 18, 205)
            cell_bg_odd = QColor(30, 22, 24, 205)
            cell_text_color = QColor("#ffffff")#FFFFFF για να ξεχωρίζουν τα γράμματα πάνω στο σκούρο background

        # ο πίνακας δημιουργεί ακριβώς τόσες γραμμές όσες είναι και τα μαθήματα που βρέθηκαν,αναλογα την ιδιότητα μας
        self.table.setRowCount(len(courses))

        for row_index, course in enumerate(courses):
            # Παραλείπουμε το course[5] που είναι το instructor_id και δεν θέλουμε να εμφανίζεται στον πίνακα,ετσι εχω φτιάξει την δομή του πίνακα courses στο db.py
            data_to_show = [course[1], course[2],
                            course[3], course[4], course[6], course[7]]
            # Τα courses[],είναι οι στήλες ID,Όνομα,Πειγραφή κλπ.
            for col_idx, data in enumerate(data_to_show):
                # Το διπλό for-loop rows,,cols μετατρέπει κάθε πληροφορία σε QTableWidgetItem
                #Δημιουργώ κελί, του βάζω χρώμα φόντου ανά γραμμή (ζυγή/μονή) και μετά χρώμα γραμμάτων για ευανάγνωστο αποτέλεσμα
                item = QTableWidgetItem(str(data)) #Το data (που μπορεί να είναι αριθμός, ημερομηνία κτλ.) μετατρέπεται σε κείμενο με str(data),
                                                   #ώστε να εμφανιστεί σωστά στο κελί.

                #Βάζω διαφορετικό background στις ζυγές και μονές γραμμές
                if row_index % 2 == 0:
                    item.setBackground(cell_bg_even)
                else:
                    item.setBackground(cell_bg_odd)
                item.setForeground(cell_text_color)

                if col_idx == 0:
                    # Αν είμαστε στην πρώτη στήλη,αποθηκεύω κρυφά το course[0],που ειναι το id που θέλω
                    item.setData(Qt.UserRole, course[0])

                # κάνει τα κελιά "μόνο για ανάγνωση" μέσα στον πίνακα,ο χρήστης μπορεί μόνο να τα επιλέξει αλλά όχι να γράψει μέσα τους
                item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                self.table.setItem(row_index, col_idx, item)

            # Δημιουργία των Icons,χρησιμοποιούμε color_active για το εφέ όταν το κουμπί είναι πατημένο/ενεργό
            view_icon = qta.icon('fa5s.folder-open',
                                 color="#C6AE39", color_active="#ffee32")
            unenroll_icon = qta.icon(
                'fa5s.times-circle', color="#954545", color_active='#e74c3c')

            # Container για δύο κουμπιά
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            # setContentsMargins(left, top, right, bottom)
            actions_layout.setContentsMargins(2, 0, 2, 0)
            actions_layout.setSpacing(15)  # Απόσταση μεταξύ των κουμπιών
            actions_layout.setAlignment(Qt.AlignCenter)

            # Κουμπί Διαλέξεων
            lecture_btn = QPushButton("")
            lecture_btn.setIcon(view_icon)
            lecture_btn.setToolTip("Διαλέξεις")
            lecture_btn.setFixedSize(32, 32)
            lecture_btn.setStyleSheet(styles.lecture_btn_style())
            lecture_btn.setCursor(Qt.PointingHandCursor)
            lecture_btn.clicked.connect(
                lambda _, course_id=course[0]: self.open_lectures(course_id))

            # Κουμπί Απεγγραφής (μόνο για students)
            if not self.admin:
                unenroll_btn = QPushButton("")
                unenroll_btn.setIcon(unenroll_icon)
                unenroll_btn.setToolTip("Απεγγραφή")
                unenroll_btn.setFixedSize(32, 32)
                unenroll_btn.setStyleSheet(styles.unenroll_btn_style())
                unenroll_btn.setCursor(Qt.PointingHandCursor)
                unenroll_btn.clicked.connect(
                    lambda _, course_id=course[0]: self.unenroll_from_course(course_id))
                actions_layout.addWidget(lecture_btn)
                actions_layout.addWidget(unenroll_btn)
            else:
                actions_layout.addWidget(lecture_btn)

            self.table.setCellWidget(row_index, 6, actions_widget)

        # Δεν αλλάζουμε τις resize modes εδώ γιατί είναι ήδη ορισμένες στη create_course_list_page
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

# -------------------------------------------------------------------------------------------------------------------------------------------------------------------
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
            QMessageBox.warning(self, "Προειδοποίηση",
                                "Παρακαλώ συμπληρώστε όλα τα πεδία.")
            return

        create_course(name, description, category,
                      instructor, start_date, end_date)
        self.update_course_list()
        self.clear_inputs()

    def delete_course(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Προειδοποίηση",
                                "Παρακαλώ επιλέξτε ένα μάθημα για διαγραφή.")
            return

        # Παίρνουμε το αντικείμενο της πρώτης στήλης
        item = self.table.item(row, 0)
        # Ανακτούμε το κρυφό ID που αποθηκεύσαμε με το UserRole
        course_id = item.data(Qt.UserRole)

        reply = QMessageBox.question(self, 'Επιβεβαίωση', f'Είστε βέβαιοι ότι θέλετε να διαγράψετε το μάθημα με ID {course_id};',
                                     # Την δεύτερη φορά που βάζουμε την επιλογή No(QMessageBox.No) την εχουμε ουσιαστικά προεπιλέξει και με ενα enter επιλεγουμε το Οχι
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            delete_course(course_id)
            self.update_course_list()

    def update_course(self, course_id):
        # .strip()Αφαιρεί όλους τους κενούς χαρακτήρες (whitespace) από την αρχή και το τέλος ενός string
        name = self.name_input.text().strip()
        description = self.description_input.text().strip()
        category = self.category_input.text().strip()
        instructor = self.instructor_input.text().strip()
        start_date = self.start_date_input.text().strip()
        end_date = self.end_date_input.text().strip()

        if not all([name, description, category, instructor, start_date, end_date]):
            QMessageBox.warning(self, "Προειδοποίηση",
                                "Παρακαλώ συμπληρώστε όλα τα πεδία.")
            return

        update_course(course_id, name, description, category,
                      instructor, start_date, end_date)
        # Ανανεωνει τον πίνακα με τα μαθήματα για να εμφανιστούν οι αλλαγές που κάναμε
        self.update_course_list()
        self.clear_inputs()  # Καθαρίζει τα πεδία κειμένου μετά την ενημέρωση του μαθήματος για να μην μπερδεύει τον Admin αν θέλει να προσθέσει νέο μάθημα ή να ενημερώσει κάποιο άλλο
        # Εφόσον κάνουμε την Ενημέρωση του μαθήματος επαναφέρει το UI στην αρχική του κατάσταση (Reset)
        self.add_course_btn.setText("➕ Προσθήκη Μαθήματος")
        self.add_course_btn.clicked.disconnect()
        self.add_course_btn.clicked.connect(self.add_course)

    def clear_inputs(self):
        for field in [self.name_input, self.description_input, self.category_input, self.instructor_input, self.start_date_input, self.end_date_input]:
            field.clear()

    def open_lectures(self, course_id):
        # Δημιουργούμε την σελίδα δυναμικά
        lectures_page = LecturesPage(
            course_id, admin=self.admin, parent_window=self)
        self.content_stack.addWidget(lectures_page)
        self.content_stack.setCurrentWidget(lectures_page)

    def open_quiz_selection_dialog(self):
        dialog = StudentQuizSelectionDialog(self.user_id, self)
        dialog.exec_()

    def open_create_quiz_course_selection(self):
        # Ανοίγει ένα παράθυρο για να διαλέξει ο Admin σε ποιο μάθημα θέλει να προσθέσει Quiz
        dialog = AdminQuizCourseSelectionDialog(self)
        if dialog.exec_() == QDialog.Accepted:  # Αν ο χρήστης πάτησε "ΟΚ" ή "Επιλογή" και δεν έκλεισε απλά το παράθυρο
            selected_course_id = dialog.get_selected_course_id()
            if selected_course_id:  # Αν το μαθημα που επελεξε υπάρχει,τότε ανοίγει το παράθυρο δημιουργίας Quiz για αυτό το μάθημα
                self.open_create_quiz_dialog(selected_course_id)

    def open_create_quiz_dialog(self, course_id):
        # Αν έγραφα QuizDialog(course_id, self) θα ήταν το ίδιο ακριβώς, αλλά έτσι είναι πιο ξεκάθαρο
        dialog = QuizDialog(course_id=course_id, parent=self)
        # parent=self, το νέο παράθυρο να ξέρει ότι "γονέας" του είναι το κεντρικό παράθυρο διαχείρισης,
        # α)δηλαδή λεμε οτι το συγκεκριμένο παραθυρο ανηκει στο κεντρικο παράθυρο με τον πίνακα μαθηματων κλπ. ωστόσο αν ο χρήστης κλείσει το κεντρικό παράθυρο διαχείρισης,
        #  η Qt θα κλείσει και θα διαγράψει αυτόματα από τη μνήμη και όλα τα ανοιχτά Dialogs που έχουν οριστεί ως «παιδιά» του για να μην τρέχουν στο παρασκήνιο.
        # β)Το παράθυρο-παιδί προσπαθεί να εμφανιστεί πάνω και στο κέντρο του γονέα του.
        # γ)Όταν καλείς το dialog.exec_() ο χρήστης δεν μπορεί να κλικάρει πίσω στον πίνακα των μαθημάτων όσο το QuizDialog είναι ανοιχτό
        if dialog.exec_() == QDialog.Accepted:
            new_quiz_id = dialog.created_quiz_id
            question_dialog = AddMultipleQuestionsDialog(
                new_quiz_id, parent=self)
            question_dialog.exec_()
        self.update_course_list()

    def go_back(self):
        from main_window import MainWindow
        # Αν η τιμη role είναι admin, τότε το ρόλο που θα περάσουμε στο MainWindow θα είναι "admin", διαφορετικά θα είναι "student"
        role = "admin" if self.admin else "student"
        self.close()
        self.main_window = MainWindow(role)
        self.main_window.show()

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
            cursor.execute(
                "INSERT INTO quizzes (course_id, title, description) VALUES (?, ?, ?)", (self.course_id, title, desc))
            conn.commit()
            self.created_quiz_id = cursor.lastrowid
            conn.close()
            self.accept()
        # Εμφανίζει ένα κόκκινο εικονίδιο με "X" (το σύμβολο του κρίσιμου σφάλματος).Σταματάει τη ροή του προγράμματος μέχρι ο χρήστης να πατήσει "OK"
        except Exception as e:
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

        self.title = QLabel(
            f"Ερώτηση {self.current_question} από {self.total_questions}")
        self.layout.addWidget(self.title)

        self.question_input = QLineEdit()
        self.question_input.setPlaceholderText("Ερώτηση")
        self.layout.addWidget(self.question_input)

        self.option_a = QLineEdit()
        self.option_a.setPlaceholderText("Επιλογή A")
        self.option_b = QLineEdit()
        self.option_b.setPlaceholderText("Επιλογή B")
        self.option_c = QLineEdit()
        self.option_c.setPlaceholderText("Επιλογή C")
        self.option_d = QLineEdit()
        self.option_d.setPlaceholderText("Επιλογή D")
        self.correct_option = QLineEdit()
        self.correct_option.setPlaceholderText("Σωστή (A, B, C, D)")

        for w in [self.option_a, self.option_b, self.option_c, self.option_d, self.correct_option]:
            # Δημιουργεί μια προσωρινή ομάδα που περιέχει τα κουμπιά ή τα πεδία κειμένου των επιλογών (A, B, C, D) και της σωστής απάντησης
            self.layout.addWidget(w)

        self.submit_btn = QPushButton("Υποβολή Ερώτησης")
        self.submit_btn.clicked.connect(self.submit_question)
        self.layout.addWidget(self.submit_btn)
        self.setLayout(self.layout)

    # ΕΛΕΓΧΟΣ ΟΤΙ ΟΙ ΕΠΙΛΟΓΕΣ ΕΧΟΥΝ ΣΥΜΠΛΗΡΩΘΕΙ ΚΑΙ ΟΤΙ Η ΣΩΣΤΗ ΑΠΑΝΤΗΣΗ ΕΙΝΑΙ ΜΙΑ ΑΠΟ ΤΙΣ 4 ΕΠΙΛΟΓΕΣ, ΠΡΙΝ ΠΡΟΣΠΑΘΗΣΕΙ ΝΑ ΤΗΝ ΠΡΟΣΘΕΣΕΙ ΣΤΗ ΒΑΣΗ ΔΕΔΟΜΕΝΩΝ. ΑΝ Ο ΕΛΕΓΧΟΣ ΑΠΟΤΥΧΕΙ, ΕΜΦΑΝΙΖΕΤΑΙ ΕΝΑ ΜΗΝΥΜΑ ΠΡΟΕΙΔΟΠΟΙΗΣΗΣ ΚΑΙ Η ΕΡΩΤΗΣΗ ΔΕΝ ΠΡΟΣΤΕΘΗΚΕ.
    def submit_question(self):
        q = self.question_input.text().strip()
        ans = [self.option_a.text(), self.option_b.text(),
               self.option_c.text(), self.option_d.text()]
        correct = self.correct_option.text().strip().upper()

        if not q or not all(ans) or correct not in ['A', 'B', 'C', 'D']:
            QMessageBox.warning(self, "Σφάλμα", "Συμπληρώστε σωστά τα πεδία.")
            return

        success = add_question_to_quiz(self.quiz_id, q, *ans, correct)
        if success:
            # Εμφανίζει τον αριθμο της τρέχουσας ερωτησης που φτιαχνουμε και το αυξανει καθε φορα σύμφωνα με τον συνολικό αριθμό ερωτήσεων(π.χ.Ερωτηση 2 από 4)
            if self.current_question < self.total_questions:
                self.current_question += 1
                self.title.setText(
                    f"Ερώτηση {self.current_question} από {self.total_questions}")
                for w in [self.question_input, self.option_a, self.option_b, self.option_c, self.option_d, self.correct_option]:
                    w.clear()  # Θεωρητικά w= ενα widget από τα πεδία ερωτήσεων και επιλογών, οπότε με το w.clear() καθαρίζουμε όλα τα πεδία για να γράψουμε την επόμενη ερώτηση
            else:
                QMessageBox.information(
                    self, "Τέλος", "Όλες οι ερωτήσεις προστέθηκαν.")
                self.accept()
