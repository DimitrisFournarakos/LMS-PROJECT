from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QMessageBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from db import get_all_courses, get_quizzes_by_course, get_statistics_for_quiz

class AdminTotalQuizStatsWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        label = QLabel("📊 Συνολικά Στατιστικά ανά Μάθημα")
        layout.addWidget(label)

        self.course_list = QListWidget()
        self.course_list.itemClicked.connect(self.load_stats_for_course)
        layout.addWidget(self.course_list)

        self.canvas = FigureCanvas(Figure(figsize=(5, 3)))
        self.ax = self.canvas.figure.subplots()
        layout.addWidget(self.canvas)

        self.load_courses()

    def load_courses(self):
        courses = get_all_courses()
        self.course_list.clear()
        for course in courses:
            self.course_list.addItem(f"{course[0]} - {course[1]}")

    def load_stats_for_course(self, item):
        course_id = int(item.text().split(" - ")[0])
        quizzes = get_quizzes_by_course(course_id)
        labels = []
        averages = []

        for quiz in quizzes:
            stats = get_statistics_for_quiz(quiz['quiz_id'])
            if stats["count"] > 0:
                labels.append(quiz['title'])
                averages.append(stats['average'])

        self.ax.clear()
        if not labels:
            QMessageBox.information(self, "Χωρίς δεδομένα", "Δεν υπάρχουν βαθμολογίες για τα quiz αυτού του μαθήματος.")
            self.canvas.draw()
            return

        x = list(range(len(labels)))
        self.ax.bar(x, averages, color="cornflowerblue")
        self.ax.set_xticks(x)
        self.ax.set_xticklabels(labels, rotation=45, ha='right')
        self.ax.set_title("Μέσοι Όροι Βαθμολογιών ανά Quiz")
        self.ax.set_ylabel("Βαθμός (%)")
        self.ax.set_ylim(0, 100)

        self.canvas.figure.tight_layout()
        self.canvas.draw()
