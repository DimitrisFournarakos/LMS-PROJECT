from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QPushButton, QMessageBox, QListWidgetItem, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon
from db import get_enrolled_courses, get_quizzes_by_course
from quiz_functions.quiz_execution_dialog import QuizExecutionDialog
from styles_css import styles


class StudentQuizSelectionDialog(QWidget):
    def __init__(self, student_id, parent_window=None):
        super().__init__(parent_window)
        self.student_id = student_id
        self.parent_window = parent_window
        self.current_quiz_widget = None
        
        self.course_item_icon_path = "icons/quiz-list-book.png" #Εικονίδιο για τα μαθήματα στη λίστα
        self.quiz_item_icon_path = "icons/quiz-exam.png" #Εικονίδιο για τα διαθέσιμα quizzes

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.layout.setSpacing(15)

        # Header
        self.layout.addWidget(styles.window_title_frame_style(
            " Online Εξέταση - Επιλογή Quiz",
            icon_path="icons/online-test-title.png"
        ))

        # Main content area
        main_container = QFrame()
        main_container.setStyleSheet(styles.student_quiz_main_container_style())
        content_layout = QVBoxLayout(main_container)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)

        # Instruction label with icon
        instruction_row = QHBoxLayout()
        instruction_row.setSpacing(8)
        instruction_row.setContentsMargins(10, 10, 10, 10)

        # Icon
        instruction_icon = QLabel()
        instruction_icon.setFixedSize(40, 40)
        icon_pixmap = QPixmap("icons/help-icon.png")       
        instruction_icon.setPixmap(icon_pixmap.scaled(38, 38, Qt.KeepAspectRatio, Qt.SmoothTransformation))   

        # Text
        instruction = QLabel("Επιλέξτε ένα μάθημα και ένα quiz για να ξεκινήσετε την εξέταση")
        instruction.setStyleSheet(styles.student_quiz_instruction_style())
        instruction.setWordWrap(True) #Αν το layout δεν έχει αρκετό πλάτος, το κείμενο θα χωριστεί σε δύο ή περισσότερες γραμμές αντί να χαθεί.

        # Add to layout
        instruction_row.addWidget(instruction_icon, 0)
        instruction_row.addWidget(instruction, 1)
        content_layout.addLayout(instruction_row)

        # Inline ενημερωτικό πλαίσιο 
        self.inline_alert_frame = QFrame()
        self.inline_alert_frame.setObjectName("inlineAlertFrame")
        self.inline_alert_frame.setStyleSheet(styles.student_quiz_inline_alert_style())
        inline_alert_layout = QHBoxLayout(self.inline_alert_frame)
        inline_alert_layout.setContentsMargins(12, 10, 12, 10)
        inline_alert_layout.setSpacing(8)

        self.inline_alert_icon = QLabel("⚠️")
        self.inline_alert_icon.setStyleSheet(styles.student_quiz_inline_alert_icon_style())
        self.inline_alert_icon.setAlignment(Qt.AlignTop)
        self.inline_alert_text = QLabel()
        self.inline_alert_text.setWordWrap(True)
        self.inline_alert_text.setStyleSheet(styles.student_quiz_inline_alert_text_style())

        inline_alert_layout.addWidget(self.inline_alert_icon, 0)
        inline_alert_layout.addWidget(self.inline_alert_text, 1)
        self.inline_alert_frame.setVisible(False)
        content_layout.addWidget(self.inline_alert_frame)

        # Ενιαίο κατακόρυφο container: πρώτα μαθήματα και αμέσως μετά quiz.
        selection_layout = QVBoxLayout()
        selection_layout.setSpacing(12)

        course_container = self._create_selection_group("Μαθήματα", "icons/education.png")
        self.course_list = QListWidget()
        self.course_list.setStyleSheet(styles.student_quiz_list_style())
        self.course_list.itemClicked.connect(self.load_quizzes)
        course_layout = course_container.layout()
        course_layout.addWidget(self.course_list)
        selection_layout.addWidget(course_container, 2)

        quiz_container = self._create_selection_group("Διαθέσιμα Quiz", "icons/online-test.png")
        self.quiz_list = QListWidget()
        self.quiz_list.setSpacing(3)
        self.quiz_list.setStyleSheet(styles.student_quiz_list_style())

        quiz_layout = quiz_container.layout()
        quiz_layout.addWidget(self.quiz_list)
        selection_layout.addWidget(quiz_container, 3)

        content_layout.addLayout(selection_layout, 1)

        self.layout.addWidget(main_container)
        self.load_courses()

    def _create_selection_group(self, title, icon_path):
        """Δημιουργεί ένα container με header και λίστα επιλογών."""
        group = QFrame()
        group.setObjectName("studentQuizSelectionGroup")
        group.setStyleSheet(styles.student_quiz_group_style())
        layout = QVBoxLayout(group)
        layout.setContentsMargins(16, 14, 16, 16)
        layout.setSpacing(12)

        # Ο header διαχωρίζει οπτικά τον τύπο των επιλογών από τη λίστα.
        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        icon_label = QLabel()
        icon_label.setPixmap(QIcon(icon_path).pixmap(24, 24))
        title_label = QLabel(title)
        title_label.setObjectName("studentQuizSelectionTitle")
        header.addWidget(icon_label)
        header.addWidget(title_label)
        header.addStretch()
        layout.addLayout(header)

        return group

    def _show_inline_alert(self, message):
        """Εμφανίζει inline μήνυμα ενημέρωσης μέσα στο ίδιο interface ότι δεν υπάρχουν διαθέσιμα quizzes.(Online Εξέταση - Επιλογή Quiz)"""
        self.inline_alert_text.setText(message)
        self.inline_alert_frame.setVisible(True)

    def _hide_inline_alert(self):
        """Κρύβει το inline μήνυμα ενημέρωσης μέσα στο ίδιο interface ότι δεν υπάρχουν διαθέσιμα quizzes."""
        self.inline_alert_text.clear()
        self.inline_alert_frame.setVisible(False)

    def _add_empty_message(self, list_widget, message):
        """Εμφανίζει πληροφοριακό μήνυμα που δεν μπορεί να επιλεγεί σαν quiz."""
        empty_item = QListWidgetItem(message)
        empty_item.setData(Qt.UserRole, None)
        empty_item.setFlags(Qt.NoItemFlags)
        list_widget.addItem(empty_item)

    def load_courses(self):
        """Φορτώνει τα μαθήματα του φοιτητή"""
        self._hide_inline_alert()
        courses = get_enrolled_courses(self.student_id)
        self.course_list.clear()
        self.quiz_list.clear()
        
        if not courses:
            self._add_empty_message(self.course_list, "Δεν έχετε εγγραφεί σε κανένα μάθημα.")
            return
        
        for course in courses:
            item_text = f"{course[1]}"
            item = QListWidgetItem(item_text)
            course_icon = QIcon(self.course_item_icon_path)          
            item.setIcon(course_icon)
            item.setData(Qt.UserRole, course[0])  # Store course_id
            self.course_list.addItem(item)

        # Επιλέγουμε το πρώτο μάθημα για να εμφανιστούν αμέσως τα διαθέσιμα quiz.
        self.course_list.setCurrentRow(0)
        self.load_quizzes(self.course_list.currentItem())

    def load_quizzes(self, item):
        """Φορτώνει τα quizzes του επιλεγμένου μαθήματος"""
        self._hide_inline_alert()
        course_id = item.data(Qt.UserRole)
        quizzes = get_quizzes_by_course(course_id)
        self.quiz_list.clear()
        
        if not quizzes:
            self._add_empty_message(self.quiz_list, "Δεν υπάρχουν διαθέσιμα quiz για αυτό το μάθημα.")
            return
        
        for quiz in quizzes:
            item = QListWidgetItem()
            item.setData(Qt.UserRole, quiz['quiz_id'])
            quiz_row = self._create_quiz_row(quiz['title'], quiz['quiz_id'])
            item.setSizeHint(quiz_row.sizeHint())
            self.quiz_list.addItem(item)
            self.quiz_list.setItemWidget(item, quiz_row)

    def _create_quiz_row(self, title, quiz_id):
        """Δημιουργεί μία γραμμή quiz με το κουμπί έναρξης δεξιά."""
        row = QFrame()
        row.setObjectName("studentQuizRow")
        row.setStyleSheet(styles.student_quiz_row_style())

        row.setMinimumHeight(50) #Ορίζουμε ελάχιστο ύψος για να μην συμπιέζεται το row μέσα στο scroll area
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(10, 6, 10, 6) #Ρυθμίζουμε τα margins ώστε να αφήνουν αέρα γύρω από τα στοιχεία
        row_layout.setSpacing(10)#Ρυθμίζουμε το spacing ώστε να υπάρχει απόσταση μεταξύ των στοιχείων
        row_layout.setAlignment(Qt.AlignVCenter) #Κεντράρουμε κάθετα τα στοιχεία μέσα στο row

        icon_label = QLabel()
        icon_label.setPixmap(QIcon(self.quiz_item_icon_path).pixmap(20, 20))
        icon_label.setFixedWidth(22)
        icon_label.setAlignment(Qt.AlignVCenter)

        title_label = QLabel(title)
        title_label.setWordWrap(True)
        title_label.setObjectName("studentQuizRowTitle")
        title_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        start_button = QPushButton("Έναρξη")
        start_button.setObjectName("quizRowStartButton")
        start_button.setStyleSheet(styles.student_quiz_row_button_style())
        start_button.setFixedSize(78, 32)
        start_button.clicked.connect(lambda checked=False, selected_quiz_id=quiz_id:self.start_selected_quiz(selected_quiz_id))
        start_button.setCursor(Qt.PointingHandCursor)
        

        row_layout.addWidget(icon_label, 0, alignment=Qt.AlignVCenter)
        row_layout.addWidget(title_label, 1, alignment=Qt.AlignVCenter)
        row_layout.addWidget(start_button, 0, alignment=Qt.AlignVCenter)

        return row

    def start_selected_quiz(self, quiz_id=None):
        """Ξεκινάει το επιλεγμένο quiz"""
        self._hide_inline_alert()
        if quiz_id is None:
            selected = self.quiz_list.currentItem()
            quiz_id = selected.data(Qt.UserRole) if selected else None

        if quiz_id is None:
            self._show_inline_alert("Παρακαλώ επιλέξτε ένα ενεργό quiz.")
            return
        
        # Δημιουργία του Quiz widget με try-except
        try:
            self.current_quiz_widget = QuizExecutionDialog(
                student_id=self.student_id, 
                quiz_id=quiz_id, 
                parent=self.parent_window, 
                selection_page=self
            )
            
            # Έλεγχος αν έχουν φορτωθεί ερωτήσεις
            if not self.current_quiz_widget.questions or len(self.current_quiz_widget.questions) == 0:
                self._show_inline_alert(
                    "Το επιλεγμένο quiz δεν έχει διαθέσιμες ερωτήσεις αυτή τη στιγμή. "
                    "Παρακαλώ επιλέξτε ένα άλλο quiz."
                )
                self.current_quiz_widget.deleteLater()
                self.current_quiz_widget = None
                return

            # Ενσωμάτωση στο content stack
            if self.parent_window and hasattr(self.parent_window, 'content_stack'):
                self.parent_window.content_stack.addWidget(self.current_quiz_widget)
                self.parent_window.content_stack.setCurrentWidget(self.current_quiz_widget)
                self.setVisible(False)
        
        except Exception as e:
            QMessageBox.critical(self," Σφάλμα",f"Δεν ήταν δυνατό να ξεκινήσει το quiz.\n\nΛεπτομέρεια: {str(e)}")

    def show_selection_again(self):
        """Επιστροφή στην επιλογή μετά το τέλος του quiz"""
        if self.current_quiz_widget:
            self.parent_window.content_stack.removeWidget(self.current_quiz_widget)
            self.current_quiz_widget.deleteLater()
            self.current_quiz_widget = None
        
        self._hide_inline_alert()
        self.quiz_list.clear()
        self.setVisible(True)
        
        if self.parent_window and hasattr(self.parent_window, 'content_stack'):
            self.parent_window.content_stack.setCurrentWidget(self)

