import sqlite3
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QRadioButton,QPushButton, QMessageBox, QButtonGroup, QFrame, QProgressBar)
from db import save_quiz_result
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

        self.questions = self.load_questions()
        
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
        main_container.setStyleSheet("background-color: #f5f5f5;")
        content_layout = QVBoxLayout(main_container)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(len(self.questions))
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #34495e;
                border-radius: 8px;
                text-align: center;
                background-color: #ecf0f1;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 6px;
            }
        """)
        content_layout.addWidget(self.progress_bar)

        # Question card
        question_card = QFrame()
        question_card.setStyleSheet("background: white; border-radius: 10px; padding: 20px; border: 1px solid #ddd;")
        question_card.setMinimumHeight(400)
        question_layout = QVBoxLayout(question_card)
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
        content_layout.addWidget(question_card)

        # Action buttons layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.submit_btn = self._create_button("✓ Υποβολή Απάντησης", "#27ae60")
        self.submit_btn.clicked.connect(self.submit_answer)
        button_layout.addWidget(self.submit_btn)

        self.prev_btn = self._create_button("← Προηγούμενη", "#34495e")
        self.prev_btn.clicked.connect(self.previous_question)
        button_layout.addWidget(self.prev_btn)

        self.back_quiz_btn = self._create_button("← Πίσω", "#e74c3c")
        self.back_quiz_btn.clicked.connect(self.go_back_to_selection)
        button_layout.addWidget(self.back_quiz_btn)

        self.next_btn = self._create_button("Επόμενη →", "#3498db")
        self.next_btn.clicked.connect(self.next_question)
        button_layout.addWidget(self.next_btn)

        self.final_btn = self._create_button("🎯 Τελική Υποβολή", "#27ae60")
        self.final_btn.clicked.connect(self.finish_quiz)
        self.final_btn.setVisible(False)
        button_layout.addWidget(self.final_btn)

        content_layout.addLayout(button_layout)

        self.outer_layout.addWidget(main_container)

        self.show_question()

    def setup_header(self):
        """Δημιουργεί το header frame με τίτλο"""
        header_frame = styles.window_title_frame_style(
            " Online Εξέταση Quiz",
            icon_path="icons/online-test-title.png"
        )
        self.outer_layout.addWidget(header_frame)

    def _create_option_button(self, label):
        """Δημιουργεί ένα styled option button"""
        btn = QRadioButton()
        btn.setStyleSheet("""
            QRadioButton {
                font-size: 16px;
                color: #2c3e50;
                padding: 12px;
                background-color: #ecf0f1;
                border-radius: 8px;
                border: 2px solid #bdc3c7;
                margin: 5px 0px;
            }
            QRadioButton:hover {
                background-color: #d5dbdb;
                border: 2px solid #3498db;
            }
            QRadioButton:checked {
                background-color: #3498db;
                color: white;
                border: 2px solid #2980b9;
            }
        """)
        return btn

    def _create_button(self, text, color):
        """Δημιουργεί ένα styled button"""
        btn = QPushButton(text)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 15px;
                font-size: 14px;
                font-weight: bold;
                cursor: pointer;
                min-height: 40px;
            }}
            QPushButton:hover {{
                background-color: {self._lighten_color(color)};
            }}
            QPushButton:pressed {{
                background-color: {self._darken_color(color)};
            }}
            QPushButton:disabled {{
                background-color: #bdc3c7;
                color: #7f8c8d;
            }}
        """)
        return btn

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

    def load_questions(self):
        """Φορτώνει τις ερωτήσεις για το quiz"""
        conn = sqlite3.connect("lms.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT question_text, option_a, option_b, option_c, option_d, correct_option
            FROM questions
            WHERE quiz_id = ?
            ORDER BY question_id
        """, (self.quiz_id,))
        results = cursor.fetchall()
        conn.close()
        return results

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
            QMessageBox.warning(self, "Προσοχή", "Παρακαλώ επιλέξτε μια απάντηση.")
            return False

        self.user_answers[self.current_index] = selected
        return True

    def submit_answer(self):
        """Υποβάλλει την τρέχουσα απάντηση"""
        if not self.save_answer():
            return
        QMessageBox.information(
            self,
            "✓ Απάντηση Υποβλήθηκε",
            f"Υποβάλατε την απάντηση: {self.user_answers[self.current_index]}"
        )

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
        confirm = QMessageBox.question(
            self, 
            "Επιβεβαίωση", 
            "Θέλετε σίγουρα να εγκαταλείψετε το quiz;\nΟι απαντήσεις δεν θα αποθηκευτούν.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            if self.selection_page:
                self.selection_page.show_selection_again()

    def finish_quiz(self):
        """Ολοκληρώνει το quiz και υπολογίζει τη βαθμολογία"""
        if not self.save_answer():
            return

        # Υπολογισμός σωστών απαντήσεων
        correct_count = 0
        for idx, user_ans in self.user_answers.items():
            correct = self.questions[idx][5].upper()
            if user_ans == correct:
                correct_count += 1

        total = len(self.questions)
        score = round((correct_count / total) * 100, 2)
        
        # Αποθήκευση αποτελέσματος
        save_quiz_result(self.student_id, self.quiz_id, score)
        
        # Εμφάνιση αποτελέσματος
        result_msg = f""" ✓ QUIZ ΟΛΟΚΛΗΡΩΘΗΚΕ           
                            Σωστές Απαντήσεις: {correct_count}/{total}
                            Βαθμολογία: {score}%

                            {'🎉 Διακρίθηκες!' if score >= 70 else '✓ Καλή απόδοση' if score >= 50 else '⚠️ Χρειάζεται περισσότερη προσπάθεια'}
                    """
        
        QMessageBox.information(self, "Ολοκλήρωση Quiz", result_msg)
        
        # Επιστροφή στο selection page
        if self.selection_page:
            self.selection_page.show_selection_again()
