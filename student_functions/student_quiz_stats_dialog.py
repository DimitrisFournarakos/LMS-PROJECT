from PyQt5.QtWidgets import QVBoxLayout, QLabel, QListWidget,QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from db import get_enrolled_courses, get_student_scores_by_course

class StudentQuizStatsPage(QWidget):
    def __init__(self, student_id, parent_window = 'CourseManagementWindow' ):
        super().__init__()
        self.student_id = student_id
        self.parent_window = parent_window #Κρατάμε αναφορά για να γυρνάμε πίσω

        self.layout = QVBoxLayout(self)

        self.label = QLabel("Τα στατιστικά μου")
        self.label.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50;")
        self.layout.addWidget(self.label)

        self.course_list = QListWidget()
        self.course_list.setFixedHeight(150) #Περιορίζω το ύψος για να χωράει το γράφημα
        self.course_list.itemClicked.connect(self.load_stats_for_course)
        self.layout.addWidget(self.course_list)

        #Matplotlib Γράφημα
        self.canvas = FigureCanvas(Figure(figsize=(5, 4)))
        self.ax = self.canvas.figure.subplots()
        self.layout.addWidget(self.canvas)

        self.load_courses()


    def load_courses(self):
        courses = get_enrolled_courses(self.student_id)
        self.course_list.clear()
        for course in courses:
            self.course_list.addItem(f"{course[0]} - {course[1]}")

    #ΕΜΦΑΝΙΖΩ ΤΟΝ ΜΕΣΟ ΟΡΟ ΤΩΝ STUDENT ΔΙΠΛΑ ΣΤΟ ΓΡΑΦΗΜΑ ΜΕ ΤΑ ΣΤΑΤΙΣΤΙΚΑ ΤΩΝ ΒΑΘΜΩΝ
    def load_stats_for_course(self, item):
        course_id = int(item.text().split(" - ")[0])
        results = get_student_scores_by_course(self.student_id, course_id)

        self.ax.clear()
        if not results:
            self.canvas.draw()
            return

        labels = [res['title'] for res in results]
        scores = [res['score'] for res in results]
        average_score = sum(scores) / len(scores)

        x = list(range(len(labels)))
        self.ax.bar(x, scores, color="mediumpurple")
        self.ax.set_title("Βαθμολογίες Quiz")
        self.ax.set_ylabel("Βαθμός (%)")
        self.ax.set_ylim(0, 100) #Προσαρμογή στο 100%
        self.ax.set_xticks(x)
        self.canvas.figure.subplots_adjust(bottom=0.3)

        #Εμφάνιση μέσου όρου δεξιά στο γράφημα
        self.ax.text(0.95, 0.95,
                    f"Μέσος Όρος:\n{average_score:.2f}%",
                    horizontalalignment='right',
                    verticalalignment='top',
                    transform=self.ax.transAxes,
                    fontsize=10,
                    bbox=dict(facecolor='lightyellow', edgecolor='gray', alpha=0.8))
        self.canvas.draw()



