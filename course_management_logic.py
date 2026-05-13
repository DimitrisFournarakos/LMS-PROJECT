"""
Λογική διαχείρισης μαθημάτων (προσθήκη, διαγραφή, ενημέρωση).
Αυτό το αρχείο περιέχει τις μεθόδους που χειρίζονται τις λειτουργίες CRUD για μαθήματα.
"""

from PyQt5.QtWidgets import QMessageBox, QDialog
from PyQt5.QtCore import Qt
from db import (create_course, delete_course as db_delete_course, update_course as db_update_course, unenroll_user_from_course)
from lectures_functions.lectures_functions import LecturesPage
from quiz_functions.quiz_selectiondialog import AdminQuizCourseSelectionDialog
from quiz_dialogs import QuizDialog, AddMultipleQuestionsDialog


class CourseManagementLogic:
    """Mixin class που περιέχει τη λογική διαχείρισης μαθημάτων"""

    def add_course(self):
        """Προσθέτει ένα νέο μάθημα στη βάση δεδομένων"""
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
        """Διαγράφει το επιλεγμένο μάθημα"""
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Προειδοποίηση",
                                "Παρακαλώ επιλέξτε ένα μάθημα για διαγραφή.")
            return

        item = self.table.item(row, 0)
        course_id = item.data(Qt.UserRole)

        reply = QMessageBox.question(
            self, 'Επιβεβαίωση', 
            f'Είστε βέβαιοι ότι θέλετε να διαγράψετε το μάθημα με ID {course_id};',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            db_delete_course(course_id)
            self.update_course_list()

    def update_course(self, course_id):
        """Ενημερώνει τα στοιχεία ενός υπάρχοντος μαθήματος"""
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

        db_update_course(course_id, name, description, category,
                         instructor, start_date, end_date)
        self.update_course_list()
        self.clear_inputs()
        
        # Reset του κουμπιού προσθήκης
        self.add_course_btn.setText("➕ Προσθήκη Μαθήματος")
        self.add_course_btn.clicked.disconnect()
        self.add_course_btn.clicked.connect(self.add_course)

    def clear_inputs(self):
        """Καθαρίζει όλα τα πεδία κειμένου"""
        for field in [self.name_input, self.description_input, self.category_input, 
                     self.instructor_input, self.start_date_input, self.end_date_input]:
            field.clear()

    def unenroll_from_course(self, course_id):
        """Αφαιρεί τον χρήστη από ένα μάθημα"""
        success = unenroll_user_from_course(self.user_id, course_id)

        if success:
            self.update_course_list()
            if hasattr(self, 'enroll_page'):
                self.enroll_page.load_courses()

    def open_lectures(self, course_id):
        """Ανοίγει τη σελίδα διαλέξεων για ένα μάθημα"""
        lectures_page = LecturesPage(
            course_id, admin=self.admin, parent_window=self)
        self.content_stack.addWidget(lectures_page)
        self.content_stack.setCurrentWidget(lectures_page)

    def open_create_quiz_course_selection(self):
        """Ανοίγει διάλογο για επιλογή μαθήματος και δημιουργία Quiz"""
        dialog = AdminQuizCourseSelectionDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            selected_course_id = dialog.get_selected_course_id()
            if selected_course_id:
                self.open_create_quiz_dialog(selected_course_id)

    def open_create_quiz_dialog(self, course_id):
        """Ανοίγει τη φόρμα δημιουργίας Quiz"""
        dialog = QuizDialog(course_id=course_id, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            new_quiz_id = dialog.created_quiz_id
            question_dialog = AddMultipleQuestionsDialog(
                new_quiz_id, parent=self)
            question_dialog.exec_()
        self.update_course_list()
