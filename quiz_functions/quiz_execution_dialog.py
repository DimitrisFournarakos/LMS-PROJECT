from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,QScrollArea, QRadioButton, QPushButton, QButtonGroup, QFrame, QProgressBar, QSizePolicy)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
from db import save_quiz_result, get_questions_by_quiz_id
from styles_css import styles


class QuizExecutionDialog(QWidget):
    def __init__(self, student_id, quiz_id, parent=None, selection_page=None):
        super().__init__(parent)
        self.student_id = student_id
        self.quiz_id = quiz_id
        self.selection_page = selection_page

        self.setWindowTitle("Online Εξέταση")
        self.setGeometry(100, 100, 900, 700)
        self.setStyleSheet(styles.get_main_window_style())

        self.outer_layout = QVBoxLayout(self)
        self.outer_layout.setContentsMargins(15, 15, 15, 15)
        self.outer_layout.setSpacing(15)

        self.questions = get_questions_by_quiz_id(self.quiz_id)
        
        # Έλεγχος για κενά ή μη διαθέσιμα quizzes
        if not self.questions:
            self.questions = []  # Κρατούμε το list κενό ώστε η διεπαφή να μην κρασάρει
            return  # Απλή επιστροφή χωρίς κλείσιμο της διεπαφής

        self.current_index = 0
        self.user_answers = {}

        # TOP HEADER FRAME με τίτλο
        self.setup_header()

        # MAIN CONTENT AREA
        main_container = QFrame()
        main_container.setStyleSheet("background-color: white; border-radius: 12px; border: 1px solid #ddd;")
        content_layout = QVBoxLayout(main_container)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)

        # Inline ενημερωτικό πλαίσιο για warnings / confirmations / results
        self.inline_alert_frame = QFrame()
        self.inline_alert_frame.setObjectName("quizExecutionAlertFrame")
        self.inline_alert_frame.setStyleSheet(styles.quiz_execution_inline_alert_style())
        inline_alert_layout = QHBoxLayout(self.inline_alert_frame)
        inline_alert_layout.setContentsMargins(12, 10, 12, 10)
        inline_alert_layout.setSpacing(12)

        # Icon at left
        self.inline_alert_icon = QLabel("⚠️")
        self.inline_alert_icon.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        inline_alert_layout.addWidget(self.inline_alert_icon, 0)

        # Centered message label (allows wrap for result messages)
        self.inline_alert_text = QLabel()
        self.inline_alert_text.setObjectName("quizExecutionAlertText")
        self.inline_alert_text.setWordWrap(True)
        self.inline_alert_text.setAlignment(Qt.AlignCenter)
        self.inline_alert_text.setStyleSheet("padding: 2px 0px; background-color: #fff4e5;")
        inline_alert_layout.addWidget(self.inline_alert_text, 1)

        # Buttons on the right (compact)
        btns_container = QFrame()
        btns_container.setStyleSheet("background-color: #fff4e5;")
        btns_layout = QHBoxLayout(btns_container)
        btns_layout.setContentsMargins(0, 0, 0, 0)
        btns_layout.setSpacing(8)

        self.inline_alert_yes_btn = self._create_button("Ναι", "#27ae60")
        self.inline_alert_yes_btn.setStyleSheet(styles.quiz_execution_inline_alert_button_style("#27ae60", compact=True))
        self.inline_alert_yes_btn.clicked.connect(self._handle_inline_alert_yes)

        self.inline_alert_no_btn = self._create_button("Όχι", "#34495e")
        self.inline_alert_no_btn.setStyleSheet(styles.quiz_execution_inline_alert_button_style("#34495e", compact=True))
        self.inline_alert_no_btn.clicked.connect(self._hide_inline_alert)

        self.inline_alert_close_btn = self._create_button("Επιστροφή", "#3498db")
        self.inline_alert_close_btn.setStyleSheet(styles.quiz_execution_inline_alert_button_style("#3498db", compact=True))
        self.inline_alert_close_btn.clicked.connect(self._handle_inline_alert_close)

        btns_layout.addWidget(self.inline_alert_yes_btn)
        btns_layout.addWidget(self.inline_alert_no_btn)
        btns_layout.addWidget(self.inline_alert_close_btn)

        inline_alert_layout.addWidget(btns_container, 0)

        self._inline_alert_mode = None
        self._inline_alert_callback = None
        self._hide_inline_alert()
        content_layout.addWidget(self.inline_alert_frame)

        # Back button row: place the back (X) button above the progress bar, right-aligned and top
        try:
            back_row = QHBoxLayout()
            back_row.setContentsMargins(0, 0, 0, 0)
            back_row.addStretch()
            # ensure back_quiz_btn exists (created in setup_header)
            if hasattr(self, 'back_quiz_btn') and self.back_quiz_btn:
                back_row.addWidget(self.back_quiz_btn, 0, Qt.AlignTop | Qt.AlignRight)
            content_layout.addLayout(back_row)
        except Exception:
            pass

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(len(self.questions))
        self.progress_bar.setStyleSheet(styles.progress_bar_style())
        content_layout.addWidget(self.progress_bar)

        # Question card
        self.question_card = QFrame()
        self.question_card.setStyleSheet("background: white; border-radius: 10px; padding: 20px; border: 1px solid #ddd;")
        self.question_card.setMinimumHeight(400)
        question_layout = QVBoxLayout(self.question_card)
        question_layout.setSpacing(12)

        self.question_label = QLabel()
        self.question_label.setWordWrap(True)
        self.question_label.setStyleSheet("font-size: 18px; color: #2c3e50; font-weight: bold;")
        question_layout.addWidget(self.question_label)

        question_layout.addSpacing(15)

        # Options with styled buttons
        self.options_group = QButtonGroup(self)
        self.option_a = self._create_option_button("A")
        self.option_b = self._create_option_button("B")
        self.option_c = self._create_option_button("C")
        self.option_d = self._create_option_button("D")

        for btn in [self.option_a, self.option_b, self.option_c, self.option_d]:
            question_layout.addWidget(btn)
            self.options_group.addButton(btn)

        question_layout.addStretch()
        content_layout.addWidget(self.question_card)

        # Action buttons layout: left controls, spacer, right primary actions
        # Action buttons layout: left controls, spacer, right primary actions
        self.button_layout = QHBoxLayout()
        self.button_layout.setSpacing(12)

        self.prev_btn = self._create_button("← Προηγούμενη", "#34495e")
        self.prev_btn.clicked.connect(self.previous_question)
        self.prev_btn.setToolTip("Προηγούμενη ερώτηση")
        self.prev_btn.setMinimumWidth(150)
        self.button_layout.addWidget(self.prev_btn)

        self.button_layout.addStretch()

        self.next_btn = self._create_button("Επόμενη →", "#3498db")
        self.next_btn.clicked.connect(self.next_question)
        self.next_btn.setToolTip("Επόμενη ερώτηση")
        self.next_btn.setMinimumWidth(160)
        self.button_layout.addWidget(self.next_btn)

        self.final_btn = self._create_button(" Τελική Υποβολή", "#27ae60")
        self.final_btn.clicked.connect(self.finish_quiz)
        self.final_btn.setVisible(False)
        self.final_btn.setToolTip("Ολοκληρώστε και υποβάλετε το quiz")
        self.final_btn.setMinimumWidth(180)
        self.button_layout.addWidget(self.final_btn)

        self.content_layout_ref = content_layout
        content_layout.addLayout(self.button_layout)

        self.outer_layout.addWidget(main_container)

        self.show_question()

    def setup_header(self):
        """Δημιουργεί το header frame με τίτλο"""
        header_frame = styles.window_title_frame_style(
            " Online Εξέταση Quiz",
            icon_path="icons/online-test-title.png"
        )

        # Δημιουργία back_button με εικονίδιο
        close_btn = QPushButton()
        close_btn.setToolTip("Επιστροφή")
        close_btn_icon = QIcon("icons/close-window.png")
        close_btn.setIcon(close_btn_icon)
        close_btn.setIconSize(QSize(32, 32))
        close_btn.setStyleSheet(styles.lectures_back_btn_style())
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setFixedSize(26, 26)
        close_btn.clicked.connect(self.go_back_to_selection)

        # Expose as back_quiz_btn so other code can reference it if needed
        self.back_quiz_btn = close_btn

        self.outer_layout.addWidget(header_frame)

    def _create_option_button(self, label):
        """Δημιουργεί ένα styled option button"""
        btn = QRadioButton()
        btn.setStyleSheet(styles.option_button_quiz_style())
        return btn

    def _create_button(self, text, color):
        """Δημιουργεί ένα styled button"""
        btn = QPushButton(text)
        # Prefer shared style from styles module for consistent look
        try:
            btn.setStyleSheet(styles.student_quiz_button_style(color))
        except Exception:
            # fallback simple styling
            btn.setStyleSheet(f"background-color: {color}; color: white; border: none; border-radius: 6px; padding: 10px 15px; font-size:14px; font-weight:bold;")

        btn.setMinimumHeight(44)
        btn.setMinimumWidth(140)
        btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        return btn

    def _set_inline_alert_state(self, kind):
        self.inline_alert_frame.setStyleSheet(styles.quiz_execution_inline_alert_style(kind))
        
        if kind == "success":
            self.inline_alert_icon.setText("✅")
            self.inline_alert_text.setStyleSheet("padding: 2px 0px; background-color: #fff4e5;")
        elif kind == "info":
            self.inline_alert_icon.setText("ℹ️")
            self.inline_alert_text.setStyleSheet("padding: 2px 0px; background-color: #fff4e5;")
        elif kind == "confirm":
            self.inline_alert_icon.setText("❓")
            
        else:
            self.inline_alert_icon.setText("⚠️")
            self.inline_alert_text.setStyleSheet("padding: 2px 0px; background-color: #fff4e5;")

    def _show_inline_alert(self, message, kind="warning", mode="message", callback=None):
        self._inline_alert_mode = mode
        self._inline_alert_callback = callback
        self._set_inline_alert_state(kind)
        self.inline_alert_text.setText(message)
        self.inline_alert_yes_btn.setVisible(mode == "confirm")
        self.inline_alert_no_btn.setVisible(mode == "confirm")
        self.inline_alert_close_btn.setVisible(mode == "result")
        self.inline_alert_frame.setVisible(True)

    def _hide_inline_alert(self):
        self.inline_alert_text.clear()
        self._inline_alert_mode = None
        self._inline_alert_callback = None
        self.inline_alert_frame.setVisible(False)

    def _handle_inline_alert_yes(self):
        callback = self._inline_alert_callback
        self._hide_inline_alert()
        if callback:
            callback()

    def _handle_inline_alert_close(self):
        callback = self._inline_alert_callback
        self._hide_inline_alert()
        if callback:
            callback()

    @staticmethod
    def _lighten_color(hex_color):
        """Ανοιχτοποιεί ένα χρώμα"""
        hex_color = hex_color.lstrip('#')
        r, g, b = [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]
        r = min(255, int(r * 1.2))
        g = min(255, int(g * 1.2))
        b = min(255, int(b * 1.2))
        return f'#{r:02x}{g:02x}{b:02x}'

    @staticmethod
    def _darken_color(hex_color):
        """Σκοτεινοποιεί ένα χρώμα"""
        hex_color = hex_color.lstrip('#')
        r, g, b = [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]
        r = int(r * 0.85)
        g = int(g * 0.85)
        b = int(b * 0.85)
        return f'#{r:02x}{g:02x}{b:02x}'

    def show_question(self):
        """Εμφανίζει την τρέχουσα ερώτηση"""
        q = self.questions[self.current_index]
        
        # Ενημέρωση progress bar
        self.progress_bar.setValue(self.current_index + 1)
        
        # Ενημέρωση ερώτησης
        self.question_label.setText(f"Ερώτηση {self.current_index + 1} από {len(self.questions)}\n\n{q[0]}")
        
        # Ενημέρωση επιλογών
        self.option_a.setText(f"A.  {q[1]}")
        self.option_b.setText(f"B.  {q[2]}")
        self.option_c.setText(f"C.  {q[3]}")
        self.option_d.setText(f"D.  {q[4]}")

        # Αποεπιλογή όλων των κουμπιών
        self.options_group.setExclusive(False)
        for btn in self.options_group.buttons():
            btn.setChecked(False)
        self.options_group.setExclusive(True)

        # Επαναφορά προηγούμενης απάντησης αν υπάρχει
        if self.current_index in self.user_answers:
            selected = self.user_answers[self.current_index]
            idx = ord(selected) - 65
            if 0 <= idx <= 3:
                self.options_group.buttons()[idx].setChecked(True)

        # Ενημέρωση κουμπιών πλοήγησης
        self.prev_btn.setEnabled(self.current_index > 0)
        self.next_btn.setVisible(self.current_index < len(self.questions) - 1)
        
        if self.current_index == len(self.questions) - 1:
            self.next_btn.setVisible(False)
            self.final_btn.setVisible(True)
            self.progress_bar.setVisible(False)
        else:
            self.next_btn.setVisible(True)
            self.final_btn.setVisible(False)

    def save_answer(self):
        """Αποθηκεύει την τρέχουσα απάντηση"""
        selected = None
        for i, btn in enumerate(self.options_group.buttons()):
            if btn.isChecked():
                selected = chr(65 + i)  # A=65, B=66, κλπ.
                break

        if not selected:
            self._show_inline_alert("Παρακαλώ επιλέξτε μια απάντηση πριν συνεχίσετε.", kind="warning")
            return False

        self._hide_inline_alert()
        self.user_answers[self.current_index] = selected
        return True

    def next_question(self):
        """Μετάβαση στην επόμενη ερώτηση"""
        if not self.save_answer():
            return
        if self.current_index < len(self.questions) - 1:
            self.current_index += 1
            self.show_question()

    def previous_question(self):
        """Μετάβαση στην προηγούμενη ερώτηση"""
        if self.current_index > 0:
            self.current_index -= 1
            self.show_question()

    def go_back_to_selection(self):
        """Επιστροφή στο quiz selection page"""
        self._show_inline_alert(
            "<span style='font-size:16px; '><b>Επιβεβαίωση:</b> Θέλετε σίγουρα να εγκαταλείψετε το quiz; Οι απαντήσεις δεν θα αποθηκευτούν αν δεν έχετε πατήσει Τελική Υποβολή.</span>",
            kind="confirm",
            mode="confirm",
            callback=self._return_to_selection
        )

    def _return_to_selection(self):
        if self.selection_page:
            self.selection_page.show_selection_again()

    def display_results(self, correct_count, total, score, mistakes):
        """Δημιουργεί και εμφανίζει το frame αποτελεσμάτων"""
        # Κρύψιμο του question card και των κουμπιών πλοήγησης
        self.question_card.setVisible(False)
        self.prev_btn.setVisible(False)
        self.next_btn.setVisible(False)
        self.final_btn.setVisible(False)
        # Δημιουργία results frame
        results_frame = QFrame()
        results_frame.setObjectName("quizResultsFrame")
        results_frame.setStyleSheet("""
            QFrame#quizResultsFrame {
                background-color: #ffffff;
                border: 1px solid #d9e2ec;
                border-radius: 14px;
            }
        """)
        try:
            styles.apply_shadow(results_frame, blur=20, x=0, y=4, alpha=35)
        except Exception:
            pass

        results_layout = QVBoxLayout(results_frame)
        results_layout.setSpacing(14)
        results_layout.setContentsMargins(22, 8, 8, 22)

        title_label = QLabel("Quiz Results")
        title_label.setStyleSheet("font-size: 25px; font-weight: 700; border: none; color: #1f2937; min-height: 55px;")
        title_label.setAlignment(Qt.AlignCenter)
        results_layout.addWidget(title_label)

        summary_frame = QFrame()
        summary_frame.setObjectName("quizResultsSummaryFrame")
        summary_frame.setStyleSheet("""
            QFrame#quizResultsSummaryFrame {
                background-color: #f8fafc;
                border: 1px solid #e5e7eb;
                border-radius: 10px;
            }
        """)
        summary_layout = QHBoxLayout(summary_frame)
        summary_layout.setContentsMargins(14, 12, 14, 12)
        summary_layout.setSpacing(16)

        total_label = QLabel(f"{correct_count}/{total}")
        total_label.setAlignment(Qt.AlignCenter)
        if score >= 70:
            score_color = "#166534"
            score_bg = "#dcfce7"
        elif score >= 50:
            score_color = "#1d4ed8"
            score_bg = "#dbeafe"
        else:
            score_color = "#b45309"
            score_bg = "#fef3c7"

        total_label.setStyleSheet(f"font-size: 22px; font-weight: 700; padding-left: 14px; padding-right: 14px; border-radius: 8px; color: {score_color}; background-color: {score_bg};")
        summary_layout.addWidget(total_label, 0)

        total_text = QLabel("Σωστές Απαντήσεις")
        total_text.setStyleSheet(f"font-size: 16px; color: #6b7280; padding-left: 14px; border-radius: 8px; font-weight: 700; color: {score_color}; background-color: {score_bg};")
        summary_layout.addWidget(total_text, 1)

        score_badge = QLabel(f"{score:.0f}%")
        score_badge.setAlignment(Qt.AlignCenter)
        if score >= 70:
            score_color = "#166534"
            score_bg = "#dcfce7"
        elif score >= 50:
            score_color = "#1d4ed8"
            score_bg = "#dbeafe"
        else:
            score_color = "#b45309"
            score_bg = "#fef3c7"

        score_badge.setStyleSheet(f"""
            font-size: 22px;
            font-weight: 700;
            color: {score_color};
            background-color: {score_bg};
            border-radius: 10px;
            padding: 8px 14px;
            min-width: 80px;
        """)
        summary_layout.addWidget(score_badge, 0)

        results_layout.addWidget(summary_frame)

        metrics_frame = QFrame()
        metrics_frame.setObjectName("quizResultsMetricsFrame")
        metrics_frame.setStyleSheet("""
            QFrame#quizResultsMetricsFrame {
                background-color: #f8fafc;
                border: 1px solid #e5e7eb;
                border-radius: 10px;
            }
        """)
        metrics_layout = QHBoxLayout(metrics_frame)
        metrics_layout.setContentsMargins(14, 12, 14, 12)
        metrics_layout.setSpacing(14)

        achieved_label = QLabel("Απόδοση")
        achieved_label.setStyleSheet("font-size: 16px; padding-left: 14px; padding-right: 14px; border-radius: 8px; font-weight: 700; color: #111827; border: 1px solid #e5e7eb;")
        metrics_layout.addWidget(achieved_label)

        if score >= 70:
            message = "Εξαιρετική επίδοση."
            message_color = "#166534"
            message_bg = "#f0fdf4"
            
        elif score >= 50:
            message = "Καλή απόδοση."
            message_color = "#1d4ed8"
            message_bg = "#eff6ff"
        else:
            message = "Χρειάζεται βελτίωση."
            message_color = "#92400e"
            message_bg = "#fffbeb"

        message_label = QLabel(message)
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setStyleSheet(f"""
            font-size: 16px;
            font-weight: 600;
            color: {message_color};
            background-color: {message_bg};
            border-radius: 8px;
            padding: 8px 12px;
            border: 1px solid #e5e7eb;
        """)
        achieved_label.setStyleSheet(f"font-size: 16px; font-weight: 600; color: {message_color}; background-color: {message_bg}; padding: 8px 12px; border-radius: 8px; border: 1px solid #e5e7eb;")
        metrics_layout.addWidget(message_label, 1)

        results_layout.addWidget(metrics_frame)

        
        #Frame για την Ανάλυση των Αποτελεσμάτων-Βαζουμε Scroll Area,δημιουργόντας List αν υπάρχουν πολλά λαθη και δεν χωρανε όλα μαζί.
        analysis_title = QLabel("Ανάλυση Αποτελεσμάτων")
        analysis_title.setStyleSheet("font-size: 16px; font-weight: 700; color: #374151; border: none; border-radius: 8px; padding: 10px; min-height: 30px;")
        results_layout.addWidget(analysis_title)

        if not mistakes:
            no_mistakes = QLabel("Δεν υπάρχουν λάθη. Όλες οι απαντήσεις ήταν σωστές.")
            no_mistakes.setStyleSheet("font-size: 14px; color: #166534; background-color: #ecfdf5; border: none; border-radius: 8px; padding: 10px;")
            results_layout.addWidget(no_mistakes)
        else:
            # Δημιουργία Scroll Area
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setBorder(False) if hasattr(scroll_area, 'setBorder') else None # fallback
            
            # Μοντέρνο & Διακριτικό στυλ για το Scrollbar (Ταίριασμα με την υπόλοιπη διεπαφή)
            scroll_area.setStyleSheet(styles.quiz_student_mistakes_list_style())

            # Το εσωτερικό frame που θα κρατάει τη λίστα των λαθών
            analysis_frame = QFrame()
            analysis_frame.setObjectName("quizResultsAnalysisFrame")
            analysis_frame.setStyleSheet("""
                QFrame#quizResultsAnalysisFrame {
                    background-color: #f8fafc;
                    border: 1px solid #e5e7eb;
                    border-radius: 10px;
                }
            """)
            analysis_layout = QVBoxLayout(analysis_frame)
            analysis_layout.setContentsMargins(14, 12, 14, 12)
            analysis_layout.setSpacing(10)

            for i, item in enumerate(mistakes, start=1):
                mistake_item = QFrame()
                mistake_item.setObjectName("quizResultsMistakeItem")
                mistake_item.setStyleSheet("""
                    QFrame#quizResultsMistakeItem {
                        background-color: #ffffff;
                        border: 1px solid #e5e7eb;
                        border-radius: 8px;
                    }
                """)
                mistake_layout = QVBoxLayout(mistake_item)
                mistake_layout.setContentsMargins(10, 8, 10, 8)
                mistake_layout.setSpacing(6)

                q_label = QLabel(f"Ερώτηση {i}: {item['question_text']}")
                q_label.setWordWrap(True)
                q_label.setStyleSheet("font-size: 14px; font-weight: 600; color: #111827; border: none; background: transparent;")
                mistake_layout.addWidget(q_label)

                user_label = QLabel(f"Δική σου απάντηση: {item['user_answer']}")
                user_label.setWordWrap(True)
                user_label.setStyleSheet("font-size: 14px; color: #b91c1c; border: none; background: transparent;")
                mistake_layout.addWidget(user_label)

                correct_label = QLabel(f"Σωστή απάντηση: {item['correct_answer']}")
                correct_label.setWordWrap(True)
                correct_label.setStyleSheet("font-size: 14px; color: #166534; font-weight: 600; border: none; background: transparent;")
                mistake_layout.addWidget(correct_label)

                analysis_layout.addWidget(mistake_item)

            analysis_layout.addStretch()
            
            # Σύνδεση του frame με το Scroll Area και προσθήκη στο κεντρικό layout
            scroll_area.setWidget(analysis_frame)
            results_layout.addWidget(scroll_area)

        results_layout.addStretch()
        self.content_layout_ref.addWidget(results_frame)

    def finish_quiz(self):
        """Ολοκληρώνει το quiz και υπολογίζει τη βαθμολογία"""
        if not self.save_answer():
            return

        # Υπολογισμός σωστών απαντήσεων και συλλογή λαθών
        correct_count = 0
        mistakes = []

        def format_option(option_letter, question_row):
            idx_map = {'A': 1, 'B': 2, 'C': 3, 'D': 4}
            letter = (option_letter or '').upper()
            opt_idx = idx_map.get(letter)
            if opt_idx is None:
                return "-"
            return f"{letter}. {question_row[opt_idx]}"

        for idx, user_ans in self.user_answers.items():
            question_row = self.questions[idx]
            correct = question_row[5].upper()
            if user_ans == correct:
                correct_count += 1
            else:
                mistakes.append({
                    "question_text": question_row[0],
                    "user_answer": format_option(user_ans, question_row),
                    "correct_answer": format_option(correct, question_row)
                })

        total = len(self.questions)
        score = round((correct_count / total) * 100, 2)
        
        # Αποθήκευση αποτελέσματος
        save_quiz_result(self.student_id, self.quiz_id, score)
        
        # Εμφάνιση αποτελέσματος στο νέο frame
        self.display_results(correct_count, total, score, mistakes)
