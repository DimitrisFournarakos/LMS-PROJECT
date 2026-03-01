from PyQt5.QtWidgets import QVBoxLayout, QLabel, QListWidget,QWidget,QListWidgetItem,QFrame
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from db import get_student_scores_by_course,get_courses_with_stats
from styles_css.styles import students_stats_rounded_container,students_stats_rounded_sub_list

class StudentQuizStatsPage(QWidget):
    def __init__(self, student_id, parent_window='CourseManagementWindow'):
        super().__init__()
        self.student_id = student_id
        self.parent_window = parent_window

        # Κύριο Layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(30, 20, 30, 30)
        self.main_layout.setSpacing(20)

        #Τίτλος (QLabel)
        self.label = QLabel("Τα στατιστικά μου")
        self.label.setFixedHeight(40) # Σταθερό ύψος για να μην πιάνει χώρο
        self.label.setStyleSheet("font-size: 25px; font-weight: bold; color: #2c3e50;")    
        self.main_layout.addWidget(self.label)   

        #Container για το Γράφημα (QFrame με στρογγυλεμένες γωνίες)
        self.graph_container = QFrame()
        self.graph_container.setStyleSheet(students_stats_rounded_container())
        graph_layout = QVBoxLayout(self.graph_container)
        graph_layout.setContentsMargins(15, 15, 15, 15) # Εσωτερικό κενό για το γράφημα

        # Matplotlib Γράφημα μέσα στο container
        self.canvas = FigureCanvas(Figure(figsize=(5, 4)))
        self.ax = self.canvas.figure.subplots()
        graph_layout.addWidget(self.canvas)
        
        self.main_layout.addWidget(self.graph_container, stretch=3)

        #Container για τη Λίστα (QFrame για ομοιομορφία)
        self.list_container = QFrame()
        self.list_container.setStyleSheet(students_stats_rounded_container())
        list_layout = QVBoxLayout(self.list_container)
        list_layout.setContentsMargins(10, 10, 10, 10)

        self.course_list = QListWidget()
        self.course_list.setStyleSheet(students_stats_rounded_sub_list())
        self.course_list.setMaximumHeight(180) 
        self.course_list.itemClicked.connect(self.load_stats_for_course)
        
        list_layout.addWidget(self.course_list)
        self.main_layout.addWidget(self.list_container, stretch=1)

        self.load_courses()

    def load_courses(self):
        courses = get_courses_with_stats(self.student_id)#Φερνουμε μεσω αυτής της συνάρτησεις,μόνο τα μαθηματα που έχει κανει έστω ενα quiz ο student.
        self.course_list.clear()
        for course in courses:
            item = QListWidgetItem(course[1])
            item.setData(Qt.UserRole, course[0])#Αποθηκεύω το ID του course "παρασκήνιο",Πρέπει να έχω το course_id για να βρώ το μαθημα αλλά χρησιμοποιώ setData για να κρατήσω μόνο τον τίτλο του
            self.course_list.addItem(item)

    #ΕΜΦΑΝΙΖΩ ΤΟΝ ΜΕΣΟ ΟΡΟ ΤΩΝ STUDENT ΔΙΠΛΑ ΣΤΟ ΓΡΑΦΗΜΑ ΜΕ ΤΑ ΣΤΑΤΙΣΤΙΚΑ ΤΩΝ ΒΑΘΜΩΝ
    def load_stats_for_course(self, item):
        course_id = item.data(Qt.UserRole)#Περνάμε το course_id μόνο ως κείμενο,για να εμφανιστεί στην λίστα οπως πρέπει(π.χ. Μαθηματικά Ι)
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
        self.ax.set_title("Βαθμολογίες Quiz")#Βαθμολογίες των Quiz από τα Quiz που έχει κάνει Ο ΙΔΙΟΣ ΜΑΘΗΤΗΣ!
        self.ax.set_ylabel("Βαθμός (%)")#Βαθμός καθε προσπάθειας-καθε Quiz που έκανε ο ΙΔΙΟΣ ΜΑΘΗΤΗΣ!
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




