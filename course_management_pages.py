"""
Δημιουργία των σελίδων του περιεχομένου (προφίλ, λίστα μαθημάτων, εργαλεία admin).
Αυτό το αρχείο περιέχει τις μεθόδους που κατασκευάζουν τις διάφορες σελίδες της εφαρμογής.
Οι μέθοδοι αυτές καλούνται από το κύριο παράθυρο (MainWindow) για να γεμίσουν το stack widget με το αντίστοιχο περιεχόμενο,
που αφορά ανάλογα είτε τον admin είτε τον student.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QFrame, QLabel, QLineEdit, QPushButton, QScrollArea, QGroupBox, QListWidget, QSizePolicy)
from PyQt5.QtCore import Qt
from db import ( get_user_by_id,get_student_quiz_leaderboard)
from styles_css import styles
from table_with_background import TableWithBackground
from PyQt5.QtWidgets import QHeaderView


class CourseManagementPages:
    """Mixin class που περιέχει τις μεθόδους δημιουργίας σελίδων"""

    def _styled_form_label(self, text):
        """Δημιουργεί ένα styled label για τις φόρμες"""
        label = QLabel(text)
        label.setStyleSheet("color: #1f2d3a; font-size: 15px; font-weight: 700;")
        return label

    def create_profile_page(self):
        """Σελίδα 0: Προφίλ Χρήστη (Κοινή για Admin και Student)"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(16)

        card = QFrame()
        card.setStyleSheet("background: white; border-radius: 10px; padding: 8px;")
        card.setMaximumHeight(260)
        card_layout = QVBoxLayout(card)

        user = get_user_by_id(self.user_id)

        if user:
            _, username, email, role = user
        else:
            username = "-"
            email = "-"
            role = "admin" if self.admin else "student"

        layout.addWidget(styles.window_title_frame_style(f" Καλώς Ήρθες, {username}!", icon_path="icons/welcome_icon.png"))

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
            self._create_student_profile_section(layout)

        layout.addStretch()
        self.content_stack.addWidget(page)

    def _create_student_profile_section(self, parent_layout):
        """Δημιουργεί το τμήμα leaderboard και ranks για τους φοιτητές"""
        leaderboard_group = QGroupBox()
        leaderboard_group.setStyleSheet(styles.leaderboard_scroll_style())
        leaderboard_group.setMinimumHeight(420)
        leaderboard_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        leaderboard_layout = QVBoxLayout(leaderboard_group)
        leaderboard_layout.setContentsMargins(14, 14, 14, 14)
        leaderboard_layout.setSpacing(12)

        leaderboard_title_frame = QFrame()
        leaderboard_title_frame.setObjectName("LeaderboardTitleFrame")
        leaderboard_title_frame.setStyleSheet(styles.leaderboard_title_style())
        leaderboard_title_layout = QVBoxLayout(leaderboard_title_frame)
        leaderboard_title_layout.setContentsMargins(18, 14, 18, 14)
        leaderboard_title_layout.setSpacing(4)

        leaderboard_title = QLabel("Leaderboard Quiz")
        leaderboard_title.setObjectName("LeaderboardTitleMain")
        leaderboard_subtitle = QLabel("Δες συγκεντρωμένα το ιστορικό από τα quiz αποτελέσματά σου.")
        leaderboard_subtitle.setObjectName("LeaderboardTitleSub")
        leaderboard_subtitle.setWordWrap(True)

        leaderboard_title_layout.addWidget(leaderboard_title)
        leaderboard_title_layout.addWidget(leaderboard_subtitle)
        leaderboard_layout.addWidget(leaderboard_title_frame)

        rows = get_student_quiz_leaderboard(self.user_id)
        if not rows:
            empty_label = QLabel("Δεν υπάρχουν ακόμα αποτελέσματα quiz.")
            empty_label.setStyleSheet("font-size: 16px; color: #5f6d7a; padding: 8px 2px;")
            leaderboard_layout.addWidget(empty_label)
        else:
            leaderboard_scroll = QScrollArea()
            leaderboard_scroll.setWidgetResizable(True)
            leaderboard_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            leaderboard_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            leaderboard_scroll.setFrameShape(QFrame.NoFrame)
            leaderboard_scroll.setStyleSheet(styles.leaderboard_scroll_style())

            leaderboard_content = QWidget()
            leaderboard_content.setObjectName("LeaderboardContent")
            leaderboard_content_layout = QFormLayout(leaderboard_content)
            leaderboard_content_layout.setContentsMargins(0, 0, 0, 0)
            leaderboard_content_layout.setSpacing(12)
            leaderboard_content_layout.setLabelAlignment(Qt.AlignLeft)
            leaderboard_content_layout.setFormAlignment(Qt.AlignTop)

            for row_data in rows:
                course_name, quiz_title, date_taken, score = row_data
                item_group = QGroupBox(f"{course_name} - {quiz_title}")
                item_group.setObjectName("LeaderboardItemGroup")
                item_group.setStyleSheet(styles.leaderboard_scroll_style())
                item_layout = QFormLayout(item_group)
                item_layout.setContentsMargins(16, 18, 16, 14)
                item_layout.setHorizontalSpacing(18)
                item_layout.setVerticalSpacing(10)
                item_layout.setLabelAlignment(Qt.AlignLeft)
                item_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)

                course_value = QLabel(course_name)
                quiz_value = QLabel(quiz_title)
                date_value = QLabel(date_taken)
                score_value = QLabel(f"{float(score):.2f}%")

                for value_label in (course_value, quiz_value, date_value, score_value):
                    value_label.setStyleSheet("color: #2c3e50; font-size: 15px;")

                item_layout.addRow(self._styled_form_label("Μάθημα:"), course_value)
                item_layout.addRow(self._styled_form_label("Quiz:"), quiz_value)
                item_layout.addRow(self._styled_form_label("Ημερομηνία:"), date_value)
                item_layout.addRow(self._styled_form_label("Βαθμός:"), score_value)
                leaderboard_content_layout.addRow(item_group)

            leaderboard_scroll.setWidget(leaderboard_content)
            leaderboard_layout.addWidget(leaderboard_scroll)

        # Δεξί πλαίσιο για Ranks
        self._create_ranks_section(parent_layout, leaderboard_group, rows)

    def _create_ranks_section(self, parent_layout, leaderboard_group, rows):
        """Δημιουργεί το τμήμα κατάταξης (ranks)"""
        ranks_group = QGroupBox()
        ranks_group.setStyleSheet(styles.leaderboard_scroll_style())
        ranks_group.setMinimumHeight(420)
        ranks_group.setMinimumWidth(320)
        ranks_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        ranks_layout = QVBoxLayout(ranks_group)
        ranks_layout.setContentsMargins(14, 14, 14, 14)
        ranks_layout.setSpacing(12)

        ranks_title_frame = QFrame()
        ranks_title_frame.setObjectName("LeaderboardTitleFrame")
        ranks_title_frame.setStyleSheet(styles.leaderboard_title_style())
        ranks_title_layout = QVBoxLayout(ranks_title_frame)
        ranks_title_layout.setContentsMargins(18, 14, 18, 14)
        ranks_title_layout.setSpacing(4)

        ranks_title = QLabel("Ranks")
        ranks_title.setObjectName("LeaderboardTitleMain")
        ranks_subtitle = QLabel("Συνολικός Μέσος Όρος και κατάσταση μαθημάτων")
        ranks_subtitle.setObjectName("LeaderboardTitleSub")
        ranks_subtitle.setWordWrap(True)

        ranks_title_layout.addWidget(ranks_title)
        ranks_title_layout.addWidget(ranks_subtitle)
        ranks_layout.addWidget(ranks_title_frame)

        # Υπολογισμός μέσου όρου και κατάστασης μαθημάτων
        course_scores = {}
        for row_data in rows:
            course_name = row_data[0]
            try:
                score = float(row_data[3])
            except Exception:
                score = 0.0
            course_scores.setdefault(course_name, []).append(score)

        all_scores = [s for scores in course_scores.values() for s in scores]
        if all_scores:
            overall_avg_percent = sum(all_scores) / len(all_scores)
            overall_avg = overall_avg_percent / 10.0
        else:
            overall_avg = 0.0

        # Καθορισμός Rank
        if 8 < overall_avg <= 10:
            rank_name = "Άριστα"
        elif 7 < overall_avg <= 8:
            rank_name = "Πολύ Καλά"
        elif 6 < overall_avg <= 7:
            rank_name = "Καλά"
        elif 5 <= overall_avg <= 6:
            rank_name = "Μέτρια"
        else:
            rank_name = "Χρειάζεται Περισσότερη Προσπάθεια"

        # Frame για τον Μέσο Όρο και Κατάταξη
        avg_rank_frame = QGroupBox()
        avg_rank_frame.setObjectName("LeaderboardItemGroup")
        avg_rank_frame.setStyleSheet(styles.leaderboard_scroll_style())
        avg_rank_layout = QFormLayout(avg_rank_frame)
        avg_rank_layout.setContentsMargins(16, 18, 16, 14)
        avg_rank_layout.setHorizontalSpacing(18)
        avg_rank_layout.setVerticalSpacing(10)
        avg_rank_layout.setLabelAlignment(Qt.AlignLeft)
        avg_rank_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)

        overall_label = QLabel(f"{overall_avg:.2f}/10")
        overall_label.setStyleSheet("color: #2c3e50; font-size: 15px;")
        rank_label = QLabel(rank_name)
        rank_label.setStyleSheet("color: #2c3e50; font-size: 15px;")

        avg_rank_layout.addRow(self._styled_form_label("Μέσος Όρος:"), overall_label)
        avg_rank_layout.addRow(self._styled_form_label("Κατάταξη:"), rank_label)
        ranks_layout.addWidget(avg_rank_frame)

        # Λίστες περασμένων / αποτυχημένων μαθημάτων
        passed = []
        failed = []
        for course, scores in course_scores.items():
            avg_course = sum(scores) / len(scores)
            if avg_course > 50:
                passed.append(course)
            else:
                failed.append(course)

        # Frame για Περασμένα Μαθήματα
        passed_frame = QGroupBox("Περασμένα Μαθήματα")
        passed_frame.setObjectName("LeaderboardItemGroup")
        passed_frame.setStyleSheet(styles.leaderboard_scroll_style())
        passed_layout = QVBoxLayout(passed_frame)
        passed_layout.setContentsMargins(16, 18, 16, 14)
        passed_layout.setSpacing(10)

        passed_list = QListWidget()
        if passed:
            passed_list.addItems(passed)
        else:
            passed_list.addItem("Δεν υπάρχουν περασμένα μαθήματα")
        passed_list.setStyleSheet(styles.students_stats_rounded_sub_list())
        passed_layout.addWidget(passed_list)
        ranks_layout.addWidget(passed_frame)

        # Frame για Αποτυχημένα Μαθήματα
        failed_frame = QGroupBox("Αποτυχημένα Μαθήματα")
        failed_frame.setObjectName("LeaderboardItemGroup")
        failed_frame.setStyleSheet(styles.leaderboard_scroll_style())
        failed_layout = QVBoxLayout(failed_frame)
        failed_layout.setContentsMargins(16, 18, 16, 14)
        failed_layout.setSpacing(10)

        failed_list = QListWidget()
        if failed:
            failed_list.addItems(failed)
        else:
            failed_list.addItem("Δεν υπάρχουν αποτυχημένα μαθήματα")
        failed_list.setStyleSheet(styles.students_stats_rounded_sub_list())
        failed_layout.addWidget(failed_list)
        ranks_layout.addWidget(failed_frame)

        # Τοποθέτηση side-by-side
        side_by_side = QHBoxLayout()
        side_by_side.setSpacing(18)
        side_by_side.addWidget(leaderboard_group, 3)
        side_by_side.addWidget(ranks_group, 1)
        parent_layout.addLayout(side_by_side)

    def create_course_list_page(self):
        """Σελίδα 1: Λίστα Μαθημάτων (Κοινή για Admin και Student)"""
        page = QWidget()
        layout = QVBoxLayout(page)

        layout.addWidget(styles.window_title_frame_style(
            " Τα μαθήματα μου" if not self.admin else " Πίνακας Ελέγχου Μαθημάτων",
            icon_path="icons/my_subjects.png"))

        self.table = TableWithBackground()
        self.table.setColumnCount(7)
        self.table_title_color = "#FFFFFF" if not self.admin else "#2c3e50"
        self.table.setStyleSheet(
            f"QTableWidget {{ color: {self.table_title_color}; font-family: 'Noto Sans', 'Segoe UI', Arial, sans-serif; font-size: 17px; font-weight: 600; }}")
        self.table.setHorizontalHeaderLabels(
            ["Όνομα", "Περιγραφή", "Κατηγορία", "Εκπαιδευτής", "Έναρξη", "Λήξη", "Ενέργειες"])

        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Fixed)
        self.table.setColumnWidth(6, 120)

        for i in range(6):
            self.table.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)

        self.table.cellClicked.connect(self.on_table_item_clicked)
        layout.addWidget(self.table)

        self.content_stack.addWidget(page)
        self.update_course_list()

    def create_admin_tools_page(self):
        """Σελίδα 2: Φόρμα Διαχείρισης μόνο για Admin"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(styles.window_title_frame_style("Επεξεργασία Μαθημάτων & Διαχείριση Quiz", icon_path="icons/edit_courses.png"))

        form_container = QFrame()
        form_container.setStyleSheet("background: white; border-radius: 10px; padding: 20px;")
        form_layout = QVBoxLayout(form_container)

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

        for inputs in [self.name_input, self.description_input, self.category_input, 
                      self.instructor_input, self.start_date_input, self.end_date_input]:
            form_layout.addWidget(inputs)

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
