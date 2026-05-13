"""
Κύριο παράθυρο διαχείρισης μαθημάτων (Course Management Window).
Συνδέει όλα τα επί μέρους modules και παρέχει τη κύρια λειτουργικότητα.
"""

import qtawesome as qta
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QPushButton, QStackedWidget, QTableWidgetItem)
from PyQt5.QtCore import Qt, QSize, QPropertyAnimation, QEvent, QEasingCurve, QTimer
from PyQt5.QtGui import QIcon, QColor, QCursor
from db import get_enrolled_courses, get_all_courses
from styles_css import styles
from course_management_logic import CourseManagementLogic
from course_management_pages import CourseManagementPages
from subjects_interface.subjects_available_interface import EnrollPage
from admin_functions.admin_total_quiz_widget import AdminTotalQuizStatsWidget
from student_functions.student_quiz_stats_page import StudentQuizStatsPage
from student_functions.student_quiz_selection_dialog import StudentQuizSelectionDialog


class CourseManagementWindow(QWidget, CourseManagementLogic, CourseManagementPages):
    """
    Παράθυρο διαχείρισης μαθημάτων με sidebar menu.
    Συνδυάζει λογική και UI από mixin classes.
    """
    
    def __init__(self, user_id, admin=False):
        super().__init__()
        self.user_id = user_id
        self.admin = admin
        self.setWindowTitle("Διαχείριση Μαθημάτων")
        self.setGeometry(100, 100, 1200, 820)
        self.setStyleSheet(styles.get_main_window_style())

        self.init_ui()

    def init_ui(self):
        """Αρχικοποιεί το UI του παραθύρου"""
        self.outer_layout = QVBoxLayout(self)
        self.outer_layout.setContentsMargins(0, 0, 0, 0)
        self.outer_layout.setSpacing(0)

        self.setMouseTracking(True)
        self.installEventFilter(self)

        # TOP BAR
        self.top_bar = QFrame()
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

        # SIDEBAR CONTAINER
        self.sidebar_container = QFrame()
        self.sidebar_container.setStyleSheet(styles.sidebar_style())
        self.sidebar_vbox = QVBoxLayout(self.sidebar_container)
        self.sidebar_vbox.setContentsMargins(0, 0, 0, 0)
        self.sidebar_vbox.setSpacing(0)

        # Σταθερό HEADER του sidebar
        self.sidebar_header = QFrame()
        self.sidebar_header.setFixedHeight(70)
        self.sidebar_header.setStyleSheet("background-color: #1a252f; border-bottom: 1px solid #34495e;")

        header_layout = QVBoxLayout(self.sidebar_header)

        btn_container = QHBoxLayout()
        btn_container.addStretch()

        self.sidebar_title_label = QLabel("MENU")
        self.sidebar_title_label.setAlignment(Qt.AlignCenter)
        self.sidebar_title_label.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")

        header_layout.addLayout(btn_container)
        header_layout.addWidget(self.sidebar_title_label)

        self.sidebar_vbox.addWidget(self.sidebar_header)

        # Πτυσσόμενο BODY του sidebar
        self.sidebar_body = QFrame()
        self.sidebar_body_layout = QVBoxLayout(self.sidebar_body)
        self.sidebar_body_layout.setContentsMargins(15, 5, 5, 15)

        self.setup_sidebar_buttons_to_layout(self.sidebar_body_layout)

        self.sidebar_vbox.addWidget(self.sidebar_body, 1)

        # CONTENT AREA
        self.content_stack = QStackedWidget()
        self.create_profile_page()      # Σελίδα 0: Προφίλ
        self.create_course_list_page()  # Σελίδα 1: Λίστα Μαθημάτων

        # Index 2: Admin Tools ή empty
        if self.admin:
            self.create_admin_tools_page()
        else:
            empty_widget = QWidget()
            self.content_stack.addWidget(empty_widget)

        # Index 3: Εγγραφή ή empty
        if not self.admin:
            self.enroll_page = EnrollPage(self.user_id, self)
            self.content_stack.addWidget(self.enroll_page)
        else:
            self.content_stack.addWidget(QWidget())

        # Σελίδα 4: Στατιστικά
        if self.admin:
            self.stats_page = AdminTotalQuizStatsWidget()
        else:
            self.stats_page = StudentQuizStatsPage(self.user_id, self)
        self.content_stack.addWidget(self.stats_page)

        # Σελίδα 5: Online Εξέταση (μόνο για Student)
        if not self.admin:
            self.quiz_selection_page = StudentQuizSelectionDialog(self.user_id, parent_window=self)
            self.content_stack.addWidget(self.quiz_selection_page)
        else:
            self.content_stack.addWidget(QWidget())

        # Σύνθεση κύριου layout
        self.main_content_layout.addWidget(self.sidebar_container)
        self.main_content_layout.addWidget(self.content_stack, 1)

        self.outer_layout.addLayout(self.main_content_layout)

        self.apply_filter_to_children(self.content_stack)
        self.apply_filter_to_children(self.top_bar)

    def apply_filter_to_children(self, widget):
        """Εφαρμόζει event filter σε όλα τα παιδιά ενός widget"""
        widget.installEventFilter(self)
        for child in widget.findChildren(QWidget):
            child.installEventFilter(self)

    def showEvent(self, event):
        """Ορίζει την αρχική κατάσταση του sidebar"""
        super().showEvent(event)
        self.sidebar_visible = False
        self.sidebar_header.hide()
        self.sidebar_body.show()
        self.set_sidebar_expanded(False)
        self.sidebar_container.setMinimumWidth(70)
        self.sidebar_container.setMaximumWidth(70)

    def eventFilter(self, obj, event):
        """Διαχειρίζεται το αυτόματο άνοιγμα και κλείσιμο του sidebar"""
        sidebar_hover_targets = []
        for attr_name in ["menu_btn", "btn_profile", "btn_courses", "btn_stats", "back_btn", "btn_admin", "btn_enroll", "btn_take_exam"]:
            target = getattr(self, attr_name, None)
            if target is not None:
                sidebar_hover_targets.append(target)

        if event.type() == QEvent.Enter and obj in sidebar_hover_targets:
            if not self.sidebar_visible:
                self.toggle_sidebar()
            return False

        if event.type() == QEvent.MouseButtonPress:
            if self.sidebar_visible:
                click_pos = self.mapFromGlobal(QCursor.pos())
                if click_pos.x() > self.sidebar_container.width():
                    self.toggle_sidebar()
                    return False

        return super().eventFilter(obj, event)

    def toggle_sidebar(self):
        """Εναλλάσσει το sidebar μεταξύ ανοιχτής και κλειστής κατάστασης"""
        if hasattr(self, 'animation') and self.animation.state() == QPropertyAnimation.Running:
            return

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
        self.animation.finished.connect(self.on_animation_finished)
        self.animation.start()

    def on_animation_finished(self):
        """Εκτελείται όταν τελειώνει το animation του sidebar"""
        if self.sidebar_visible:
            self.sidebar_header.show()
            self.sidebar_body.show()
            self.set_sidebar_expanded(True)
            self.sidebar_title_label.show()
            self.sidebar_header.setStyleSheet("background-color: #1a252f; border-bottom: 1px solid #34495e;")

    def set_sidebar_expanded(self, expanded):
        """Θέτει το sidebar σε expanded ή collapsed κατάσταση"""
        button_width = 250 if expanded else 40
        self.sidebar_body_layout.setContentsMargins(15, 5, 5, 15) if expanded else self.sidebar_body_layout.setContentsMargins(10, 5, 10, 15)

        buttons_with_text = [
            (self.btn_profile, " Προφίλ"),
            (self.btn_courses, " Μαθήματα"),
            (self.btn_stats, " Στατιστικά"),
            (self.back_btn, "Αποσύνδεση"),
        ]

        if self.admin and hasattr(self, 'btn_admin'):
            buttons_with_text.insert(2, (self.btn_admin, " Διαχείριση Quiz"))
        if not self.admin and hasattr(self, 'btn_enroll'):
            buttons_with_text.insert(2, (self.btn_enroll, " Εγγραφή"))
        if not self.admin and hasattr(self, 'btn_take_exam'):
            buttons_with_text.insert(2, (self.btn_take_exam, " Online Εξέταση"))

        for button, text in buttons_with_text:
            button.setText(text if expanded else "")
            button.setFixedWidth(button_width)
            button.setCursor(Qt.PointingHandCursor if expanded else Qt.ArrowCursor)

    def setup_sidebar_buttons_to_layout(self, sidebar_body_layout):
        """Δημιουργεί και τοποθετεί τα κουμπιά του sidebar"""
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

        if not self.admin:
            self.btn_take_exam = QPushButton(" Online Εξέταση")
            self.btn_take_exam.setIcon(QIcon("icons/online-test.png"))
            self.btn_take_exam.setIconSize(QSize(15, 15))
            self.btn_take_exam.setFixedSize(40, 40)
            self.btn_take_exam.setFixedWidth(250)
            self.btn_take_exam.clicked.connect(lambda: self.content_stack.setCurrentIndex(5))
            self.sidebar_body_layout.addWidget(self.btn_take_exam)

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

        self.sidebar_body_layout.addStretch(1)
        self.apply_filter_to_children(sidebar_body_layout)

        back_btn_layout = QHBoxLayout()
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

        sidebar_buttons = [self.btn_profile, self.btn_courses, self.btn_stats, self.back_btn]
        if self.admin and hasattr(self, 'btn_admin'):
            sidebar_buttons.append(self.btn_admin)
        if not self.admin and hasattr(self, 'btn_enroll'):
            sidebar_buttons.append(self.btn_enroll)
        if not self.admin and hasattr(self, 'btn_take_exam'):
            sidebar_buttons.append(self.btn_take_exam)

        for btn in sidebar_buttons:
            btn.installEventFilter(self)

    def on_table_item_clicked(self, row):
        """Διαχειρίζεται το κλικ σε ένα κελί του πίνακα μαθημάτων"""
        if self.admin:
            self.content_stack.setCurrentIndex(2)

            item_name = self.table.item(row, 0)
            course_id = item_name.data(Qt.UserRole)

            self.name_input.setText(item_name.text())
            self.description_input.setText(self.table.item(row, 1).text())
            self.category_input.setText(self.table.item(row, 2).text())
            self.instructor_input.setText(self.table.item(row, 3).text())
            self.start_date_input.setText(self.table.item(row, 4).text())
            self.end_date_input.setText(self.table.item(row, 5).text())

            self.add_course_btn.setText("📝 Ενημέρωση Μαθήματος")

            try:
                self.add_course_btn.clicked.disconnect()
            except:
                pass

            self.add_course_btn.clicked.connect(
                lambda: self.update_course(course_id))

    def update_course_list(self):
        """Ανανεώνει τη λίστα των μαθημάτων στον πίνακα"""
        if self.admin:
            courses = get_all_courses()
        else:
            courses = get_enrolled_courses(self.user_id)

        if self.admin:
            cell_bg_even = QColor(255, 248, 232, 235)
            cell_bg_odd = QColor(246, 236, 214, 235)
            cell_text_color = QColor("#2c3e50")
        else:
            cell_bg_even = QColor(12, 10, 18, 205)
            cell_bg_odd = QColor(30, 22, 24, 205)
            cell_text_color = QColor("#ffffff")

        self.table.setRowCount(len(courses))

        for row_index, course in enumerate(courses):
            data_to_show = [course[1], course[2],
                            course[3], course[4], course[6], course[7]]

            for col_idx, data in enumerate(data_to_show):
                item = QTableWidgetItem(str(data))

                if row_index % 2 == 0:
                    item.setBackground(cell_bg_even)
                else:
                    item.setBackground(cell_bg_odd)
                item.setForeground(cell_text_color)

                if col_idx == 0:
                    item.setData(Qt.UserRole, course[0])

                item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                self.table.setItem(row_index, col_idx, item)

            view_icon = qta.icon('fa5s.folder-open',
                                 color="#C6AE39", color_active="#ffee32")
            unenroll_icon = qta.icon(
                'fa5s.times-circle', color="#954545", color_active='#e74c3c')

            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(2, 0, 2, 0)
            actions_layout.setSpacing(15)
            actions_layout.setAlignment(Qt.AlignCenter)

            lecture_btn = QPushButton("")
            lecture_btn.setIcon(view_icon)
            lecture_btn.setToolTip("Διαλέξεις")
            lecture_btn.setFixedSize(32, 32)
            lecture_btn.setStyleSheet(styles.lecture_btn_style())
            lecture_btn.setCursor(Qt.PointingHandCursor)
            lecture_btn.clicked.connect(
                lambda _, course_id=course[0]: self.open_lectures(course_id))

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

        self.table.horizontalHeader().setStyleSheet(styles.get_table_header_style())

    def go_back(self):
        """Γυρίζει στο κύριο παράθυρο"""
        from main_window import MainWindow
        role = "admin" if self.admin else "student"
        self.close()
        self.main_window = MainWindow(role)
        self.main_window.show()
