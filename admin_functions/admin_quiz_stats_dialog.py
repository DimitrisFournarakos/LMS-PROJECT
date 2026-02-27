from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QListWidget, QMessageBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from db import get_quizzes_by_course, get_statistics_for_quiz

class AdminQuizStatsDialog(QDialog):
    def __init__(self, course_id, parent=None):
        super().__init__(parent)
        self.course_id = course_id
        self.setWindowTitle("📊 Στατιστικά Quiz Μαθήματος")
        self.setGeometry(200, 200, 600, 500)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.info_label = QLabel("Επέλεξε ένα quiz για να δεις στατιστικά:")
        self.layout.addWidget(self.info_label)

        self.quiz_list = QListWidget()
        self.quiz_list.itemClicked.connect(self.show_quiz_statistics)
        self.layout.addWidget(self.quiz_list)

        self.canvas = FigureCanvas(Figure(figsize=(5, 3)))
        self.ax = self.canvas.figure.subplots()
        self.layout.addWidget(self.canvas)

        self.load_quizzes()

    def load_quizzes(self):
        quizzes = get_quizzes_by_course(self.course_id)
        self.quiz_list.clear()
        for quiz in quizzes:
            self.quiz_list.addItem(f"{quiz['quiz_id']} - {quiz['title']}")

    def show_quiz_statistics(self, item):
        quiz_id = int(item.text().split(" - ")[0])
        stats = get_statistics_for_quiz(quiz_id)

        if stats["count"] == 0:
            QMessageBox.information(self, "Χωρίς αποτελέσματα", "Δεν υπάρχουν βαθμολογίες για αυτό το quiz.")
            return

        self.ax.clear()
        labels = ["Μέσος Όρος", "Ελάχιστο", "Μέγιστο"]
        values = [stats["average"], stats["min"], stats["max"]]

        bars = self.ax.bar(labels, values, color=["skyblue", "lightcoral", "lightgreen"])
        self.ax.set_ylim(0, 100)
        self.ax.set_ylabel("Βαθμός (%)")
        self.ax.set_title(f"Στατιστικά Quiz ID {quiz_id}")
        self.canvas.draw()


from db import get_all_courses

class AdminTotalQuizStatsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📊 Επιλογή Μαθήματος για Στατιστικά")
        self.setGeometry(400, 400, 800, 700)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.label = QLabel("Επέλεξε μάθημα για να δεις συνολικά στατιστικά:")
        self.layout.addWidget(self.label)

        self.course_list = QListWidget()
        self.course_list.itemClicked.connect(self.load_stats_for_course)
        self.layout.addWidget(self.course_list)

        self.canvas = FigureCanvas(Figure(figsize=(5, 3)))
        self.ax = self.canvas.figure.subplots()
        self.layout.addWidget(self.canvas)

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
        self.ax.set_title("Μέσοι Όροι Βαθμολογιών ανά Quiz")
        self.ax.set_ylabel("Βαθμός (%)")
        self.ax.set_ylim(0, 50)
        self.ax.set_xticks(x)
        
        self.canvas.draw()
