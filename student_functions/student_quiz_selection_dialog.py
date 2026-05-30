from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QPushButton, QMessageBox, QListWidgetItem, QFrame, QGroupBox)
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
        instruction_row.setContentsMargins(0, 0, 0, 0)

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

        # Inline ενημερωτικό πλαίσιο (αντί για popup)
        self.inline_alert_frame = QFrame()
        self.inline_alert_frame.setObjectName("inlineAlertFrame")
        self.inline_alert_frame.setStyleSheet(styles.student_quiz_inline_alert_style())
        inline_alert_layout = QHBoxLayout(self.inline_alert_frame)
        inline_alert_layout.setContentsMargins(12, 10, 12, 10)
        inline_alert_layout.setSpacing(8)

        self.inline_alert_icon = QLabel("⚠️")
        self.inline_alert_icon.setStyleSheet("background-color: #fff4e5; ")
        self.inline_alert_icon.setAlignment(Qt.AlignTop)
        self.inline_alert_text = QLabel()
        self.inline_alert_text.setWordWrap(True)
        self.inline_alert_text.setStyleSheet(
            "color: #8a5a00; font-size: 13px; font-weight: 500; "
            "background-color: #fff4e5; border-radius: 6px;"
        )

        inline_alert_layout.addWidget(self.inline_alert_icon, 0)
        inline_alert_layout.addWidget(self.inline_alert_text, 1)
        self.inline_alert_frame.setVisible(False)
        content_layout.addWidget(self.inline_alert_frame)

        # Two-column layout for courses and quizzes
        selection_layout = QHBoxLayout()
        selection_layout.setSpacing(15)

        # Left side: Courses
        course_container = self._create_selection_group("Μαθήματα", "icons/education.png")
        self.course_list = QListWidget()
        self.course_list.setStyleSheet(self._get_list_style())
        self.course_list.itemClicked.connect(self.load_quizzes)
        course_layout = course_container.layout()
        course_layout.addWidget(self.course_list)
        selection_layout.addWidget(course_container, 1)

        # Right side: Quizzes
        quiz_container = self._create_selection_group("Available Quizzes", "icons/online-test.png")
        self.quiz_list = QListWidget()
        self.quiz_list.setStyleSheet(self._get_list_style())
        quiz_layout = quiz_container.layout()
        quiz_layout.addWidget(self.quiz_list)
        selection_layout.addWidget(quiz_container, 1)

        content_layout.addLayout(selection_layout, 1)

        # Action buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        self.start_btn = self._create_button("🎯 Έναρξη Quiz", "#27ae60")
        self.start_btn.clicked.connect(self.start_selected_quiz)
        buttons_layout.addWidget(self.start_btn)

        self.back_btn = self._create_button("← Πίσω", "#34495e")
        self.back_btn.clicked.connect(self.go_back)
        buttons_layout.addWidget(self.back_btn)

        content_layout.addLayout(buttons_layout)

        self.layout.addWidget(main_container)
        self.load_courses()

    def _create_selection_group(self, title, icon_path):
        """Δημιουργεί ένα styled group για επιλογή"""
        group = QGroupBox(title)
        group.setStyleSheet(styles.student_quiz_group_style())
        layout = QVBoxLayout(group)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        return group

    def _get_list_style(self):
        """Επιστρέφει το styling για τις λίστες"""
        return styles.student_quiz_list_style()

    def _create_button(self, text, color):
        """Δημιουργεί ένα styled button"""
        btn = QPushButton(text)
        btn.setMinimumHeight(45)
        btn.setStyleSheet(styles.student_quiz_button_style(color))
        return btn
 

    def _show_inline_alert(self, message):
        """Εμφανίζει inline μήνυμα ενημέρωσης μέσα στο ίδιο interface ότι δεν υπάρχουν διαθέσιμα quizzes.(Online Εξέταση - Επιλογή Quiz)"""
        self.inline_alert_text.setText(message)
        self.inline_alert_frame.setVisible(True)

    def _hide_inline_alert(self):
        """Κρύβει το inline μήνυμα ενημέρωσης μέσα στο ίδιο interface ότι δεν υπάρχουν διαθέσιμα quizzes."""
        self.inline_alert_text.clear()
        self.inline_alert_frame.setVisible(False)

    def load_courses(self):
        """Φορτώνει τα μαθήματα του φοιτητή"""
        self._hide_inline_alert()
        courses = get_enrolled_courses(self.student_id)
        self.course_list.clear()
        
        if not courses:
            self.course_list.addItem("❌ Δεν έχετε εγγραφεί σε κανένα μάθημα")
            return
        
        for course in courses:
            item_text = f"{course[1]}"
            item = QListWidgetItem(item_text)
            course_icon = QIcon(self.course_item_icon_path)          
            item.setIcon(course_icon)
            item.setData(Qt.UserRole, course[0])  # Store course_id
            self.course_list.addItem(item)

    def load_quizzes(self, item):
        """Φορτώνει τα quizzes του επιλεγμένου μαθήματος"""
        self._hide_inline_alert()
        course_id = item.data(Qt.UserRole)
        quizzes = get_quizzes_by_course(course_id)
        self.quiz_list.clear()
        
        if not quizzes:
            self.quiz_list.addItem("❌ Δεν υπάρχουν ενεργά quizzes για αυτό το μάθημα")
            return
        
        for quiz in quizzes:
            item_text = f"{quiz['title']}"
            item = QListWidgetItem(item_text)
            quiz_icon = QIcon(self.quiz_item_icon_path)
            item.setIcon(quiz_icon)
            item.setData(Qt.UserRole, quiz['quiz_id'])  # Store quiz_id
            self.quiz_list.addItem(item)

    def start_selected_quiz(self):
        """Ξεκινάει το επιλεγμένο quiz"""
        self._hide_inline_alert()
        selected = self.quiz_list.currentItem()
        
        # Έλεγχος αν έχει επιλεγεί κάτι
        if not selected or "❌" in selected.text():
            self._show_inline_alert("Παρακαλώ επιλέξτε ένα ενεργό quiz.")
            return
        
        quiz_id = selected.data(Qt.UserRole)
        
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
            QMessageBox.critical(
                self,
                "❌ Σφάλμα",
                f"Δεν ήταν δυνατό να ξεκινήσει το quiz.\n\nΛεπτομέρεια: {str(e)}"
            )

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

    def go_back(self):
        """Κλείνει την ενότητα και επιστρέφει στη λίστα μαθημάτων"""
        if self.current_quiz_widget:
            self.show_selection_again()
        elif self.parent_window and hasattr(self.parent_window, 'content_stack'):
            self.parent_window.content_stack.setCurrentIndex(1)
