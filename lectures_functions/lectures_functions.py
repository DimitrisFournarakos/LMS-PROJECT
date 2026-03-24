import os
import base64
import fitz
import shutil 
from styles_css import styles
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLineEdit, QPushButton, QMessageBox,QFileDialog, QLabel, QMessageBox, QFileDialog, QLabel, QStackedWidget, QListWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView

class LecturesPage(QWidget):
    def __init__(self, course_id, admin=False, parent_window=None):
        super().__init__()
        
        self.course_id = course_id
        self.admin = admin
        self.parent_window = parent_window

        self.lectures_folder = os.path.join("lectures", f"course_{self.course_id}") #Φάκελος όπου θα αποθηκεύονται οι διαλέξεις για το συγκεκριμένο μάθημα. Π.χ. "lectures/course_123"
        self.current_pdf_doc = None #Μεταβλητή που θα κρατάει το ανοιχτό PDF object (PyMuPDF document).Ξεκινάει None γιατί στην αρχή δεν έχει ανοιχτεί κανένα PDF
        self.current_page_index = 0
        self.total_pages = 0

        # Κύριο layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 10, 15, 15)
        main_layout.setSpacing(20)

        # Τίτλος
        title = QLabel(f"Διαλέξεις Μαθήματος")
        title.setStyleSheet(
            "font-size: 25px; font-weight: bold; color: #2c3e50;")
        main_layout.addWidget(title)

        # Stacked widget για να εναλλάσσουμε μεταξύ λίστας και viewer
        self.stack = QStackedWidget()

        # --- ΣΕΛΙΔΑ 0: Λίστα Διαλέξεων ---
        lectures_container = QFrame()
        lectures_container.setStyleSheet(styles.students_stats_rounded_container())# βάζω το ίδιο στυλ με στρογγυλεμένο container από τα στατιστικά βαθμών μαθητών
        container_layout = QVBoxLayout(lectures_container)
        container_layout.setContentsMargins(15, 15, 15, 15)

        self.lectures_list = QListWidget()
        self.lectures_list.itemClicked.connect(self.on_lecture_clicked)
        self.load_lectures()
        container_layout.addWidget(self.lectures_list)

        self.stack.addWidget(lectures_container)  # Index 0

        # --- ΣΕΛΙΔΑ 1: Viewer Διάλεξης ---
        viewer_container = QFrame()
        viewer_container.setStyleSheet(styles.students_stats_rounded_container())
        viewer_layout = QVBoxLayout(viewer_container)
        viewer_layout.setContentsMargins(8, 8, 8, 8)

        # Back button
        back_btn = QPushButton("⬅️ Πίσω στις Διαλέξεις")
        back_btn.clicked.connect(self.back_to_lectures)
        viewer_layout.addWidget(back_btn)
        viewer_layout.setSpacing(10)

        # Controls πλοήγησης σελίδων για μεγάλα PDF.
        nav_layout = QHBoxLayout()
        self.prev_page_btn = QPushButton("⬅ Προηγούμενη")
        self.prev_page_btn.clicked.connect(self.show_prev_page)
        self.next_page_btn = QPushButton("Επόμενη ➡")
        self.next_page_btn.clicked.connect(self.show_next_page)
        self.page_indicator = QLabel("")
        self.page_indicator.setAlignment(Qt.AlignCenter)
        nav_layout.addWidget(self.prev_page_btn)
        nav_layout.addWidget(self.page_indicator, 1) #Μεγεθος των κουμπιών 
        nav_layout.addWidget(self.next_page_btn)

        viewer_layout.addLayout(nav_layout)
        self.prev_page_btn.setEnabled(False)
        self.next_page_btn.setEnabled(False)

        # Text area για εμφάνιση του περιεχομένου της διάλεξης
        self.lecture_content = QWebEngineView() #Χρησιμοποιώ QWebEngineView για να μπορώ να εμφανίσω το PDF ως εικόνα μέσα σε HTML, αντί να προσπαθήσω να κάνω render το PDF απευθείας που μπορεί να είναι περίπλοκο και να κρασάρει.
        self.lecture_content.setMinimumHeight(550)
        viewer_layout.addWidget(self.lecture_content, 1) #Δίνω περισσότερο ύψος στο ίδιο το pdf content widget

        self.stack.addWidget(viewer_container)  # Index 1

        main_layout.addWidget(self.stack, 1)#Δίνω περισσότερο ύψος στο stack για να πιάνει όλο το διαθέσιμο χώρο κάτω από τον τίτλο,το 1 σημαίνει "πάρε όλο τον διαθέσιμο κάθετο χώρο που έχεις"

        # Κουμπί προσθήκης (μόνο για admin)
        if self.admin:
            add_btn = QPushButton("➕ Προσθήκη Διάλεξης")
            add_btn.clicked.connect(self.add_lecture)
            main_layout.addWidget(add_btn)

    def load_lectures(self):
        """Φορτώνει τις διαλέξεις από τον φάκελο"""
        self.lectures_list.clear()

        if os.path.exists(self.lectures_folder):
            files = os.listdir(self.lectures_folder)
            if files:
                for file in files:
                    self.lectures_list.addItem(file)
            else:
                self.lectures_list.addItem("Δεν υπάρχουν διαλέξεις")
        else:
            self.lectures_list.addItem("Δεν υπάρχουν διαλέξεις")

    def on_lecture_clicked(self, item):
        """Ανοίγει τη διάλεξη που επιλέχθηκε"""
        lecture_file = item.text()

        if lecture_file == "Δεν υπάρχουν διαλέξεις":
            return

        file_path = os.path.join(self.lectures_folder, lecture_file)#Φτιάχνω το πλήρες μονοπάτι του αρχείου που επιλέχθηκε, π.χ. "lectures/course_123/lecture1.pdf"
        self.current_lecture_path = file_path

        ext = os.path.splitext(lecture_file)[1].lower()

        if ext == ".pdf":
                      
                print(f"[DEBUG] Φόρτωση PDF από: {file_path}")
                self.close_current_pdf()

                self.current_pdf_doc = fitz.open(file_path) #Ανοίγω το PDF με το fitz.open(PyMuPDF) και κρατάω το document object στην μεταβλητή self.current_pdf_doc για να μπορώ να το χρησιμοποιήσω αργότερα για να κάνω render τις σελίδες.
                self.total_pages = len(self.current_pdf_doc) #Υπολογίζω τον συνολικό αριθμό σελιδών του pdf
                self.current_page_index = 0

                if self.total_pages == 0:
                    self.close_current_pdf()
                    QMessageBox.warning(self, "Σφάλμα", "Το PDF είναι κενό")
                    return

                self.render_current_page() #Καλώ την rendr_current_page για να εμφανίσω την πρώτη σελίδα του PDF στο viewer.
            
        else:
            QMessageBox.warning(self, "Μη υποστηριζόμενο αρχείο", "Υποστηρίζονται μόνο PDF.")
            return

        # Εναλλαγή σε viewer
        self.stack.setCurrentIndex(1)

    def render_current_page(self):
        """Κάνει render την τρέχουσα σελίδα του PDF και την εμφανίζει στο QWebEngineView,"""
        """ PyMuPDF για parsing/render του PDF  &  QWebEngineView για display του τελικού HTML """

        if not self.current_pdf_doc or self.total_pages == 0:
            return

        page = self.current_pdf_doc[self.current_page_index] #Για να γίνει η εμφάνιση,παίρνω τη σελίδα με Index.
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False) #Μετατρέπει τη σελίδα σε εικόνα (raster) με get_pixmap(matrix=fitz.Matrix(2.2, 2.2)), 2x οριζόντια και 2x κάθετα,άρα η εικόνα βγαίνει πιο μεγάλη και πιο καθαρή από το default 1.0, αλλά με μεγαλύτερο κόστος σε μνήμη/χρόνο.
        img_data = pix.tobytes("png") #Παίρνει bytes PNG από το pixmap.
        img_base64 = base64.b64encode(img_data).decode("utf-8") #Κωδικοποιεί τα bytes σε base64 string για να μπορέσει να ενσωματωθεί σε HTML.

        #-----Φτιάχνω HTML που έχει img src=data:image/png;base64,... ------
        html = f"""  
        <html>
        <body style='background-color: #ffffff; margin: 0; padding: 0;'>
            <img src='data:image/png;base64,{img_base64}' style='display: block; width: 100%; height: auto; border: none;' />
        </body>
        </html>
        """
        self.lecture_content.setHtml(html) #Εμφανίζει το HTML με την εικόνα της σελίδας στο QWebEngineView. Η QWebEngineView χρησιμοποιείται σαν HTML render,ουσιαστικά του δίνω ήδη έτοιμη εικόνα σελίδας (μέσω base64 μέσα σε HTML)
        self.page_indicator.setText(f"Σελίδα {self.current_page_index + 1} / {self.total_pages}")
        self.prev_page_btn.setEnabled(self.current_page_index > 0)
        self.next_page_btn.setEnabled(self.current_page_index < self.total_pages - 1)

    def show_prev_page(self):
        if self.current_pdf_doc and self.current_page_index > 0:
            self.current_page_index -= 1
            self.render_current_page()

    def show_next_page(self):
        if self.current_pdf_doc and self.current_page_index < self.total_pages - 1:
            self.current_page_index += 1
            self.render_current_page()

    def close_current_pdf(self):
        if self.current_pdf_doc is not None:
            try:
                self.current_pdf_doc.close()
            except Exception:
                pass

        self.current_pdf_doc = None
        self.total_pages = 0
        self.current_page_index = 0
        self.page_indicator.setText("") #καθαρίζει το κείμενο του label page_indicator και το κάνει κενό,UI reset γραμμή

        #Το κουμπί εμφανίζεται “γκρι” και δεν πατιέται.
        #Τα βάζω αρχικά False γιατί στην αρχή δεν έχει φορτωθεί PDF, άρα δεν υπάρχει σελίδα για prev/next, μετά όταν φορτωθεί ένα PDF τα ενημερώνω δυναμικά μέσα στη render_current_page.
        self.prev_page_btn.setEnabled(False)
        self.next_page_btn.setEnabled(False)

    def back_to_lectures(self):
        self.close_current_pdf()
        self.stack.setCurrentIndex(0)

    def add_lecture(self):
        """Προσθέτει νέα διάλεξη (για admin)"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Επιλέξτε αρχείο")#Επιστρέφει το μονοπάτι του αρχείου που επέλεξε ο χρήστης μέσω του file dialog. Αν ο χρήστης ακυρώσει, το file_path θα είναι κενό string<--(_ , είναι “δεν με ενδιαφέρει αυτή η τιμή”).
        if file_path:
            os.makedirs(self.lectures_folder, exist_ok=True)                             #target_path είναι ο προορισμός όπου θα αντιγραφεί το αρχείο
            target_path = os.path.join(self.lectures_folder, os.path.basename(file_path))#os.path.basename(file_path): κρατάει μόνο το όνομα αρχείου, χωρίς τους φακέλους
                                                                                         #os.path.join(self.lectures_folder, ...): ενώνει τον φάκελο διαλέξεων του μαθήματος με αυτό το όνομα.
            try:
                shutil.copy(file_path, target_path) #εδώ αντιγράφει το αρχείο από την αρχική θέση (file_path) στον φάκελο μαθήματος (target_path).
                QMessageBox.information(
                    self, "Επιτυχία", "Η διάλεξη προστέθηκε.")
                self.load_lectures()
            except Exception as e:
                QMessageBox.warning(self, "Σφάλμα", f"Αποτυχία Φόρτωσης Διάλεξης: {e}")

