import textwrap
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QListWidget, QWidget, QListWidgetItem, QFrame
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from db import get_student_scores_by_course,get_courses_with_stats
from styles_css.styles import (
    students_stats_rounded_container,
    students_stats_list_style,
    window_title_frame_style,
)

class StudentQuizStatsPage(QWidget):
    def __init__(self, student_id, parent_window='CourseManagementWindow'):
        super().__init__()
        self.student_id = student_id
        self.parent_window = parent_window

        # Κύριο Layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(30, 20, 30, 30)
        self.main_layout.setSpacing(20)

        self.main_layout.addWidget(window_title_frame_style(" Τα στατιστικά μου", icon_path="icons/growth-graph.png"))

        #Container για το Γράφημα (QFrame με στρογγυλεμένες γωνίες)
        self.graph_container = QFrame()
        self.graph_container.setStyleSheet(students_stats_rounded_container())
        graph_layout = QVBoxLayout(self.graph_container)
        graph_layout.setContentsMargins(15, 15, 15, 15) # Εσωτερικό κενό για το γράφημα
        graph_layout.setSpacing(6)

        self.progress_summary = QLabel()
        self.progress_summary.setStyleSheet("color: #243b53; font-size: 14px; font-weight: 600; padding: 4px 8px;")
        graph_layout.addWidget(self.progress_summary)

        # Matplotlib Γράφημα μέσα στο container
        self.canvas = FigureCanvas(Figure(figsize=(5, 2.8)))
        self.canvas.setMinimumHeight(240)
        self.ax = self.canvas.figure.subplots()
        # Το canvas παίρνει όλο τον διαθέσιμο χώρο του graph container.
        graph_layout.addWidget(self.canvas, 1)
        
        self.main_layout.addWidget(self.graph_container, stretch=2)

        #Container για τη Λίστα (QFrame για ομοιομορφία)
        self.list_container = QFrame()
        self.list_container.setStyleSheet(students_stats_rounded_container())
        list_layout = QVBoxLayout(self.list_container)
        list_layout.setContentsMargins(10, 10, 10, 10)

        course_label = QLabel("Επίλεξε μάθημα")
        course_label.setStyleSheet("font-weight: 700; color: #243b53;")
        list_layout.addWidget(course_label)

        self.course_list = QListWidget()
        self.course_list.setObjectName("courseList")
        self.course_list.setStyleSheet(students_stats_list_style())
        self.course_list.itemClicked.connect(self.load_stats_for_course)
        list_layout.addWidget(self.course_list, 1)

        history_label = QLabel("Ιστορικό ανά Quiz")
        history_label.setStyleSheet("font-weight: 700; color: #243b53;")
        list_layout.addWidget(history_label)

        self.history_list = QListWidget()
        self.history_list.setObjectName("historyList")
        self.history_list.setStyleSheet(students_stats_list_style())
        self.history_list.setWordWrap(True)
        list_layout.addWidget(self.history_list, 1)

        self.main_layout.addWidget(self.list_container, stretch=2)

        self.load_courses()

    def load_courses(self):
        courses = get_courses_with_stats(self.student_id)#Φερνουμε μεσω αυτής της συνάρτησεις,μόνο τα μαθηματα που έχει κανει έστω ενα quiz ο student.
        self.course_list.clear()
        self.history_list.clear()
        for course in courses:
            item = QListWidgetItem(course[1])
            item.setData(Qt.UserRole, course[0])#Αποθηκεύω το ID του course "παρασκήνιο",Πρέπει να έχω το course_id για να βρώ το μαθημα αλλά χρησιμοποιώ setData για να κρατήσω μόνο τον τίτλο του
            self.course_list.addItem(item)
        
        # Επιλέγουμε αυτόματα το πρώτο μάθημα και φορτώνουμε τα στατιστικά του
        if self.course_list.count() > 0:
            first_item = self.course_list.item(0)
            self.course_list.setCurrentItem(first_item)
            self.load_stats_for_course(first_item)

    # Εμφανίζουμε την πορεία του μέσου όρου ανά quiz.
    def load_stats_for_course(self, item):
        course_id = item.data(Qt.UserRole)#Περνάμε το course_id μόνο ως κείμενο,για να εμφανιστεί στην λίστα οπως πρέπει(π.χ. Μαθηματικά Ι)
        results = get_student_scores_by_course(self.student_id, course_id)

        self.ax.clear()
        if not results:
            self.progress_summary.clear()
            self.history_list.clear()
            self.canvas.draw()
            return

        scores = [res['score'] for res in results]
        labels = [res['title'] for res in results]
        attempt_counts = [res['attempt_count'] for res in results]
        total_attempts = sum(attempt_counts)
        average_score = sum(score * count for score, count in zip(scores, attempt_counts)) / total_attempts
        best_score = max(scores)
        self.progress_summary.setText(f"Η συνολική σου επίδοση είναι {average_score:.2f}%. "f"Η καλύτερη μέση επίδοση σε quiz είναι {best_score:.2f}%.")

        attempt_numbers = list(range(1, len(scores) + 1))
        self.history_list.clear()
        for position, result in enumerate(results, start=1):
            self.history_list.addItem(f"{position}. {result['title']} - "f"Μέση επίδοση: {result['score']:.2f}%")

        self.ax.plot(
            attempt_numbers,
            scores,
            color="mediumpurple",
            marker="o",
            linewidth=2.5,
            label="Μέσος όρος quiz",
        )
        self.ax.axhline(
            average_score,
            color="#6b7280",
            linestyle="--",
            linewidth=1.5,
            label=f"Μέσος όρος ({average_score:.2f}%)",
        )
        
        self.ax.set_title("Πορεία μέσου όρου ανά Quiz")
        self.ax.set_xlabel("Quiz με χρονολογική σειρά")
        self.ax.set_ylabel("Μέσος βαθμός (%)")
        self.ax.set_ylim(0, 100)
        label_step = max(1, len(labels) // 10)
        # Κρατάμε κάθε label_step θέση, ώστε ο άξονας να παραμένει ευανάγνωστος.
        tick_positions = attempt_numbers[::label_step]
        visible_labels = [
            textwrap.fill(label, width=22)
            for label in labels[::label_step]
        ]

        self.ax.set_xticks(tick_positions)
        self.ax.set_xticklabels(visible_labels, rotation=0, ha="center", fontsize=8)
        self.ax.grid(axis="y", alpha=0.25)
        self.ax.legend(loc="lower right", fontsize=9)
        self.canvas.figure.subplots_adjust(bottom=0.22, top=0.92, left=0.1, right=0.97)


        #Εμφάνιση μέσου όρου δεξιά στο γράφημα
        self.ax.text(0.95, 0.95,
                    f"Μέσος Όρος:\n{average_score:.2f}%",
                    horizontalalignment='right',
                    verticalalignment='top',
                    transform=self.ax.transAxes,
                    fontsize=10,
                    bbox=dict(facecolor='lightyellow', edgecolor='gray', alpha=0.8))
        self.canvas.draw()




