import os
import base64
import fitz
from styles_css import styles
from db import add_lecture_to_course, get_lectures_by_course, get_lecture_pdf_by_id
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame, QPushButton, QMessageBox,QFileDialog, QLabel, QMessageBox, QFileDialog, QLabel, QStackedWidget, QListWidget, QListWidgetItem
from PyQt5.QtCore import Qt,QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWebEngineWidgets import QWebEngineView

class LecturesPage(QWidget):
    def __init__(self, course_id, admin=False, parent_window=None):
        super().__init__()
        
        self.course_id = course_id
        self.admin = admin
        self.parent_window = parent_window

        self.current_pdf_doc = None #Μεταβλητή που θα κρατάει το ανοιχτό PDF object (PyMuPDF document).Ξεκινάει None γιατί στην αρχή δεν έχει ανοιχτεί κανένα PDF
        self.current_page_index = 0
        self.total_pages = 0

        # Κύριο layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 20, 15, 15)
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
        back_btn = QPushButton("")
        back_btn_icon = QIcon("icons/close-window.png")
        back_btn.setIcon(back_btn_icon)
        back_btn.setIconSize(QSize(32, 32))
        back_btn.setStyleSheet(styles.lectures_back_btn_style())
        back_btn.setCursor(Qt.PointingHandCursor)
        back_btn.setFixedSize(52, 52) #Δίνω λίγο μεγαλύτερο μέγεθος στο κουμπί από το εικονίδιο για να είναι πιο εύκολο στο κλικ, αλλά το εικονίδιο παραμένει 44x44.
        back_btn.clicked.connect(self.back_to_lectures)

        # Controls πλοήγησης σελίδων για μεγάλα PDF.
        nav_layout = QHBoxLayout()
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(8)
        
        self.prev_page_btn = QPushButton("")
        self.prev_page_btn_icon = QIcon("icons/previous-page.png")
        self.prev_page_btn.setIcon(self.prev_page_btn_icon)
        self.prev_page_btn.setIconSize(QSize(30, 30))
        self.prev_page_btn.setStyleSheet(styles.lectures_prev_page_btn_style())
        self.prev_page_btn.clicked.connect(self.show_prev_page)
        self.prev_page_btn.setCursor(Qt.PointingHandCursor)
        self.prev_page_btn.setFixedSize(44, 44)


        self.next_page_btn = QPushButton("")
        self.next_page_btn_icon = QIcon("icons/next-page.png")
        self.next_page_btn.setIcon(self.next_page_btn_icon)
        self.next_page_btn.setIconSize(QSize(30, 30))
        self.next_page_btn.setStyleSheet(styles.lectures_next_page_btn_style())
        self.next_page_btn.clicked.connect(self.show_next_page)
        self.next_page_btn.setCursor(Qt.PointingHandCursor)
        self.next_page_btn.setFixedSize(44, 44)

        self.page_indicator = QLabel("")
        self.page_indicator.setAlignment(Qt.AlignCenter)
        nav_layout.addStretch(1)
        nav_layout.addWidget(self.prev_page_btn)
        nav_layout.addSpacing(100)  # Κενό μεταξύ prev και page_indicator
        nav_layout.addWidget(self.page_indicator)
        nav_layout.addSpacing(100)  # Κενό μεταξύ page_indicator και next
        nav_layout.addWidget(self.next_page_btn)
        nav_layout.addStretch(1)
        nav_layout.addWidget(back_btn, 0, Qt.AlignRight | Qt.AlignVCenter)

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
        """Φορτώνει τις διαλέξεις του μαθήματος από τη βάση."""
        self.lectures_list.clear()

        rows = get_lectures_by_course(self.course_id)#Επιστρέφει μια λίστα με tuples (lecture_id, display_name) για τις διαλέξεις του μαθήματος
        if not rows:
            self.lectures_list.addItem("Δεν υπάρχουν διαλέξεις")
            return

        for lecture_id, display_name in rows:
            item = QListWidgetItem(display_name)# όπου display_name είναι το file_name αν υπάρχει, αλλιώς το title, και αν και αυτό είναι NULL τότε 'lecture.pdf' λόγω του COALESCE στο SQL query. Έτσι εξασφαλίζουμε ότι πάντα θα έχουμε ένα όνομα για να εμφανίσουμε στη λίστα, ακόμα και αν δεν έχει ανέβει PDF ή δεν έχει οριστεί τίτλος.
            item.setData(Qt.UserRole, lecture_id)#Αποθηκεύω το lecture_id στο item χρησιμοποιώντας setData με ρόλο Qt.UserRole, έτσι όταν κάνω κλικ σε αυτό το item, μπορώ να ανακτήσω το lecture_id για να φορτώσω το σωστό PDF από την βάση.
            self.lectures_list.addItem(item)

    def add_lecture(self):
        """Προσθέτει νέα διάλεξη (για admin) αποθηκεύοντας το PDF στη βάση."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Επιλέξτε αρχείο", "", "PDF Files (*.pdf)") #Ανοίγει file dialog για επιλογή αρχείου.
        if file_path:
            try:
                if os.path.splitext(file_path)[1].lower() != ".pdf":#Παίρνω το extension από το όνομα αρχείου,το κάνω lowercase για ασφάλεια,(.PDF-->.pdf)
                    QMessageBox.warning(self, "Μη υποστηριζόμενο αρχείο", "Υποστηρίζονται μόνο PDF.")
                    return

                with open(file_path, "rb") as f: #Ανοίγει το αρχείο σε binary read mode,rb=read binary & Το with φροντίζει να κλείσει αυτόματα το αρχείο μετά την ανάγνωση.
                    pdf_data = f.read() #Διαβάζει όλο το PDF σε bytes (pdf_data), για αποθήκευση σε BLOB

                if not pdf_data:
                    QMessageBox.warning(self, "Σφάλμα", "Το επιλεγμένο PDF είναι κενό.")
                    return

                add_lecture_to_course(self.course_id, os.path.basename(file_path), pdf_data) #Insert στην βάση, os.path.basename(file_path) για να πάρω μόνο το όνομα αρχείου χωρίς το path, pdf_data τα δυαδικά δεδομένα του PDF για αποθήκευση στη βάση.
                QMessageBox.information(
                    self, "Επιτυχία", "Η διάλεξη προστέθηκε.")
                self.load_lectures()
            except Exception as e:
                QMessageBox.warning(self, "Σφάλμα", f"Αποτυχία Φόρτωσης Διάλεξης: {e}")

    def on_lecture_clicked(self, item):
        """Ανοίγει τη διάλεξη που επιλέχθηκε από τη βάση."""
        lecture_id = item.data(Qt.UserRole)
        if lecture_id is None:
            return

        try:
            pdf_data = get_lecture_pdf_by_id(lecture_id)
            if not pdf_data:
                QMessageBox.warning(self, "Σφάλμα", "Δεν βρέθηκαν δεδομένα PDF για τη διάλεξη.")
                return

            self.close_current_pdf()
            self.current_pdf_doc = fitz.open(stream=pdf_data, filetype="pdf")
            self.total_pages = len(self.current_pdf_doc)
            self.current_page_index = 0

            if self.total_pages == 0:
                self.close_current_pdf()
                QMessageBox.warning(self, "Σφάλμα", "Το PDF είναι κενό")
                return

            self.render_current_page()
        except Exception as e:
            QMessageBox.warning(self, "Σφάλμα", f"Αποτυχία φόρτωσης διάλεξης: {e}")
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
        image_width_percent = max(40, min(100, int(0.7 * 100)))

        #-----Φτιάχνω HTML που έχει img src=data:image/png;base64,... ------
        html = f"""  
        <html>
        <body style='background-color: #ffffff; margin: 0; padding: 0;'>
            <img src='data:image/png;base64,{img_base64}' style='display: block; width: 70%; height: auto; border: none; margin: 0 auto;' />
        </body>
        </html>
        """
        self.lecture_content.setHtml(html) #Εμφανίζει το HTML με την εικόνα της σελίδας στο QWebEngineView. Η QWebEngineView χρησιμοποιείται σαν HTML render,ουσιαστικά του δίνω ήδη έτοιμη εικόνα σελίδας (μέσω base64 μέσα σε HTML)
        self.page_indicator.setText(f"Σελίδα {self.current_page_index + 1} / {self.total_pages}")
        self.page_indicator.setStyleSheet("font-size: 23px; color: black; font-weight: 455; background: transparent; border: none;")
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


