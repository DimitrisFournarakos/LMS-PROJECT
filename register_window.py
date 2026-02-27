import re
from PyQt5.QtCore import Qt, QEvent,QSize
from PyQt5.QtGui import QFont,QIcon
from PyQt5.QtWidgets import QWidget, QLineEdit, QPushButton, QLabel, QVBoxLayout, QMessageBox,QComboBox,QAction
from db import connect_db
from styles_css.styles import input_style_register_window,input_style_role_combo_register,back_btn_style,login_register_window,login_register_user_title_style

#Αυτή την μέθοδο την έβαλα έξω από την κλάση RegisterWindow γιατί ακριβώς την ίδια θέλω να ξαναχρησιμοποιήσω στο login_window.py για το πεδίο password
#Συνεπώς,στο αρχειό login_window.py απλά θα την κάνω Import και μετά θα την καλέσω ως συναρτηση με Lambda: toggle_password_visibility(self)
def toggle_password_visibility(self):
        """Εναλλαγή ορατότητας του password όταν πατηθεί το εικονίδιο του ματιού"""
        if self.password_visible:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.eye_action.setIcon(QIcon("icons/eye_close.png"))
            self.password_visible = False
        else:
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.eye_action.setIcon(QIcon("icons/eye_open.png"))
            self.password_visible = True


class RegisterWindow(QWidget):
    def __init__(self, role=None, parent_window=None):
        #Inheritace
        super().__init__()#Καλούμε τις βασικες παραμετρους της κλάσης (role,parent_window) και ΠΡΟΣΘΕΤΟΥΜΕ-Ορίζουμε το παράθυρο εγγραφής με τίτλο, μέγεθος και μεταβλητή για το hover του κουμπιού επιστροφής
        self.role = role   #Η super() καλεί τον constructor της βασικής κλάσης (QWidget) για να αρχικοποιήσει το παράθυρο εγγραφής. Μετά, ορίζουμε τον ρόλο του χρήστη και τις παραμέτρους του παραθύρου.
        self.parent_window = parent_window
        self.host = None # Θα κρατάμε αναφορά στο LoginWindow που θέλουμε να γεμίσουμε     
        self.setWindowTitle("LMS - Εγγραφή") 
        self.setGeometry(100, 100, 300, 250)
        self.hovered_button = None  # Προσθήκη μεταβλητής για παρακολούθηση hover,οταν έχω το ποντίκι επάνω στο κουμπί να φαίνεται οτι παω να το επιλέξω

        # Αποθηκευμένα widgets / labels θα μπουν εδώ (όταν καλείται open_register)
        self.name_input = None
        self.email_input = None
        self.password_input = None
        self.role_combo = None
        self.name_error = None
        self.email_error = None
        self.password_error = None
        self.email_already_exists_error = None
        self.name_already_exists_error = None
        self.password_already_exists_error = None
        self.name_range_error = None
        self.email_range_error = None
        self.password_range_error = None

    def eventFilter(self, source, event):
        """Ανίχνευση hover πάνω στο κουμπί Επιστροφή"""
        if event.type() == QEvent.Enter:
            if source == self.back_btn:
                self.hovered_button = 'back'
        elif event.type() == QEvent.Leave:
            if source == self.back_btn:
                self.hovered_button = None
        return super().eventFilter(source, event)

    def keyPressEvent(self, event):
        """Ελέγχουμε αν πατήθηκε το πλήκτρο Enter για το κουμπί Επιστροφή"""
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            if self.hovered_button == 'back':
                self.go_back()

    def go_back(self):
            """Απλά κλείνουμε το παράθυρο εγγραφής για να επιστρέψουμε στο παράθυρο σύνδεσης"""
            self.close()


    def open_register(self,login_widget):
            """
            Γεμίζει το login_widget.login_layout με τα πεδία εγγραφής.
            Το login_widget πρέπει να είναι instance του LoginWindow (έχει clear_login_frame(), load_login_fields(), login_layout).
            """
           
            # Κρατάμε την αναφορά ώστε οι μέθοδοι να έχουν πρόσβαση στα widgets
            self.host = login_widget            
            self.host.clear_login_frame()
            
            title = QLabel(f"Εγγραφή Χρήστη \n")
            title.setFont(QFont("Segoe UI", 15, QFont.Bold))
            title.setAlignment(Qt.AlignCenter)                                              
            title.setStyleSheet(login_register_user_title_style())#Το margin δημιουργεί κενό έξω από το στοιχείο, ενώ το padding δημιουργεί κενό μέσα στο στοιχείο, μεγαλώνοντας ουσιαστικά το μέγεθος του "κουτιού" του τίτλου
            title.setFixedHeight(200)  # Εξασφαλίζει ότι ο τίτλος έχει αρκετό ύψος για να χωρέσει το κενό
            

            self.name_input = QLineEdit()
            self.name_input.setPlaceholderText("Ονοματεπώνυμο")
            self.name_input.setStyleSheet(input_style_register_window())

            name_icon = QIcon("icons/name-icon.png")
            self.name_input.addAction(name_icon, QLineEdit.TrailingPosition)
            
            self.name_error = QLabel("")
            self.name_error.setStyleSheet("color: #E74C3C; font-size: 16px; margin-left: 5px; background: none; border: none;")
            self.name_error.hide()
            
            self.email_input = QLineEdit()
            self.email_input.setPlaceholderText("Email")
            self.email_input.setStyleSheet(input_style_register_window())

            email_icon = QIcon("icons/email-icon.png")
            self.email_input.addAction(email_icon, QLineEdit.TrailingPosition)

            self.email_error = QLabel("")
            self.email_error.setStyleSheet("color: #E74C3C; font-size: 16px; margin-left: 5px; background: none; border: none;")
            self.email_error.hide()           
            
            self.password_input = QLineEdit()
            self.password_input.setPlaceholderText("Συνθηματικό (password)")
            self.password_input.setEchoMode(QLineEdit.Password)
            self.password_input.setStyleSheet(input_style_register_window())
                      
            self.password_visible = False
            self.eye_action = QAction(QIcon("icons/eye_close.png"),"", self.password_input)
            self.password_input.addAction(self.eye_action, QLineEdit.TrailingPosition)
            self.eye_action.setToolTip("Εμφάνιση/Απόκρυψη συνθηματικού")
            self.eye_action.triggered.connect(lambda: toggle_password_visibility(self))            

            self.password_error = QLabel("")
            self.password_error.setStyleSheet("color: #E74C3C; font-size: 16px; margin-left: 5px; background: none; border: none;")
            self.password_error.hide()

            # Προσθήκη επιλογής ρόλου στην εγγραφή
            self.role_combo = QComboBox()
            self.role_combo.addItems(["student", "admin"])
            self.role_combo.setCurrentText("student")  # Προεπιλογή
            self.role_combo.setStyleSheet(input_style_role_combo_register())  # Εφαρμογή στυλ στο ComboBox

            #Φτιάχνουμε ένα QLabel για messege error αν χρησιμοποιείται ήδη το email που προσπαθεί να εγγραφεί ο χρήστης
            self.email_already_exists_error = QLabel("")
            self.email_already_exists_error.setStyleSheet("color: #E74C3C; font-size: 16px; margin-left: 5px; background: none; border: none;")
            self.email_already_exists_error.hide()

            self.name_already_exists_error = QLabel("")
            self.name_already_exists_error.setStyleSheet("color: #E74C3C; font-size: 16px; margin-left: 5px; background: none; border: none;")
            self.name_already_exists_error.hide()

            self.password_already_exists_error = QLabel("")
            self.password_already_exists_error.setStyleSheet("color: #E74C3C; font-size: 16px; margin-left: 5px; background: none; border: none;")
            self.password_already_exists_error.hide()

            # QLabel για τα μηνύματα σφάλματος που αφορούν τα όρια χαρακτήρων των πεδίων εγγραφής       
            self.name_range_error = QLabel("")
            self.name_range_error.setStyleSheet("color: #E74C3C; font-size: 16px; margin-left: 5px; background: none; border: none;")
            self.name_range_error.hide()

            self.email_range_error = QLabel("")
            self.email_range_error.setStyleSheet("color: #E74C3C; font-size : 16px; margin-left: 5px; background: none; border: none;")
            self.email_range_error.hide()

            self.password_range_error = QLabel("")
            self.password_range_error.setStyleSheet("color: #E74C3C; font-size: 16px; margin-left: 5px; background: none; border: none;")
            self.password_range_error.hide()

            register_btn = QPushButton("Εγγραφή ")
            register_btn.setStyleSheet(login_register_window())
            register_btn.setCursor(Qt.PointingHandCursor)
            register_btn.clicked.connect(self.register_user)
            register_icon = QIcon("icons/register-icon.png")
            register_btn.setIcon(register_icon)
            register_btn.setIconSize(QSize(16, 16)) 
            register_btn.setLayoutDirection(Qt.RightToLeft) # Τοποθετεί το εικονίδιο στα δεξιά του κειμένου
            register_btn.clicked.connect(self.register_user)  # Συνδέουμε το κουμπί στο method της κλάσης

            back_btn = QPushButton("Επιστροφή")
            back_btn.setCursor(Qt.PointingHandCursor)
            back_btn.setStyleSheet(back_btn_style())
            
            back_btn_icon = QIcon("icons/back-icon.png")
            back_btn.setIcon(back_btn_icon)
            back_btn.setIconSize(QSize(25, 25))
            back_btn.setLayoutDirection(Qt.LeftToRight) # Τοποθετεί το εικονίδιο στα αριστερά του κειμένου
            back_btn.clicked.connect(self.host.load_login_fields)

            #Προσθήκη widgets στο layout του login_widget με την σωστή σειρά και με κενά ανάμεσά τους για καλύτερη εμφάνιση
            self.host.login_layout.addWidget(title) 
            self.host.login_layout.addSpacing(10)  # Μειώνει το κενό μεταξύ των widgets       
            self.host.login_layout.addWidget(self.name_input)
            self.host.login_layout.setSpacing(2)  # Μειώνει το κενό μεταξύ των widgets
            self.host.login_layout.addWidget(self.name_error)
            self.host.login_layout.setSpacing(1)
            self.host.login_layout.addWidget(self.name_range_error)
            self.host.login_layout.setSpacing(1)
            self.host.login_layout.addWidget(self.name_already_exists_error)
            self.host.login_layout.addSpacing(5)
            self.host.login_layout.addWidget(self.email_input)
            self.host.login_layout.setSpacing(2)  # Μειώνει το κενό μεταξύ των widgets
            self.host.login_layout.addWidget(self.email_error)
            self.host.login_layout.setSpacing(1)
            self.host.login_layout.addWidget(self.email_already_exists_error)
            self.host.login_layout.setSpacing(1)
            self.host.login_layout.addWidget(self.email_range_error)
            self.host.login_layout.setSpacing(1)
            self.host.login_layout.addWidget(self.email_already_exists_error)
            self.host.login_layout.addSpacing(5)
            self.host.login_layout.addWidget(self.password_input)
            self.host.login_layout.setSpacing(2)
            self.host.login_layout.addWidget(self.password_error)
            self.host.login_layout.setSpacing(1)
            self.host.login_layout.addWidget(self.password_range_error)
            self.host.login_layout.setSpacing(1)
            self.host.login_layout.addWidget(self.password_already_exists_error)
            self.host.login_layout.addSpacing(10)
            self.host.login_layout.addWidget(self.role_combo)
            self.host.login_layout.addSpacing(20)
            self.host.login_layout.addWidget(register_btn)
            self.host.login_layout.addSpacing(30)
            self.host.login_layout.addWidget(back_btn) 
            self.host.login_layout.addStretch(2) # <--- Αυτό θα "σπρώξει" τα πάντα προς τα πάνω

    def register_user(self):
            """
            Αυτή η μέθοδος χρησιμοποιεί τα widgets που αποθηκεύτηκαν στην self.* από το open_register.
            """        

            #Καθαρισμός Προηγούμενων Σφαλμάτων
            self.name_error.hide()
            self.email_error.hide()
            self.password_error.hide()
            self.name_range_error.hide()
            self.email_range_error.hide()
            self.password_range_error.hide()
            self.email_already_exists_error.hide()
            self.name_already_exists_error.hide()
            self.password_already_exists_error.hide()

            self.name_input.setStyleSheet(input_style_register_window())
            self.email_input.setStyleSheet(input_style_register_window())
            self.password_input.setStyleSheet(input_style_register_window())

            name = self.name_input.text()
            email = self.email_input.text()
            password = self.password_input.text()
            selected_role = self.role_combo.currentText()
            valid = True

            #Όριο χαρακτήρων για τα πεδία εγγραφής
            MIN_NAME_LEN, MAX_NAME_LEN = 3 , 64
            MIN_EMAIL_LEN, MAX_EMAIL_LEN = 1, 128
            MIN_PASSWORD_LEN, MAX_PASSWORD_LEN = 8, 128

            if len(name) < MIN_NAME_LEN or len(name) > MAX_NAME_LEN:
                self.name_range_error.setText(f"• Το ονοματεπώνυμο πρέπει να είναι μεταξύ\n {MIN_NAME_LEN} και {MAX_NAME_LEN} χαρακτήρων.")
                self.name_range_error.show()
                self.name_input.setStyleSheet(input_style_register_window() + "border: 1px solid #E74C3C;")
                valid = False

            if len(email) < MIN_EMAIL_LEN or len(email) > MAX_EMAIL_LEN:
                self.email_range_error.setText(f"• Το email πρέπει να είναι μεταξύ\n {MIN_EMAIL_LEN} και {MAX_EMAIL_LEN} χαρακτήρων.")
                self.email_range_error.show()
                self.email_input.setStyleSheet(input_style_register_window() + "border: 1px solid #E74C3C;")
                valid = False

            if len(password) < MIN_PASSWORD_LEN or len(password) > MAX_PASSWORD_LEN:
                self.password_range_error.setText(f"• Το συνθηματικό πρέπει να είναι μεταξύ\n {MIN_PASSWORD_LEN} και {MAX_PASSWORD_LEN} χαρακτήρων.")
                self.password_range_error.show()
                self.password_input.setStyleSheet(input_style_register_window() + "border: 1px solid #E74C3C;")
                valid = False
                        
            #Έλεγχος Εγκυρότητας για το πεδίο Ονοματεπώνυμο
            if not name.replace(" ", "").isalpha() :#Αφαιρούμε προσωρινά τα κενά για να ελένξουμε αν οι υπόλοιποι χαρακτήρες είναι γράμματα.
                self.name_error.setText("• Επιτρέπονται μόνο γράμματα \n (π.χ. Γιάννης Παπαδόπουλος,Nick Barner).")
                self.name_error.show()
                self.name_input.setStyleSheet(input_style_register_window()+ "border: 1px solid #E74C3C;")
                valid = False
            
            #Έλεγχος Εγκυρότητας για το πεδίο Email
            # Πρότυπο Regular Expression για έγκυρο email
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            allowed_domains = ["gmail.com","yahoo.com","outlook.com","hotmail.com","icloud.com","live.com","msn.com","yahoo.gr","gmail.gr"]
            
            if not re.match(email_pattern, email):
                self.email_error.setText("• Εισάγετε μια έγκυρη διεύθυνση email \n (π.χ. name@example.com).")
                self.email_error.show()
                self.email_input.setStyleSheet(input_style_register_window() + "border: 1px solid #E74C3C;")
                valid = False

            else:
                # Εδώ είμαστε σίγουροι ότι υπάρχει '@' και ελενγχουμε στην συνέχεια αν υπάρχει το σωστό domain και αν το email καταλήγει σε .com, .gr, .net ή .org
                domain = email.split("@")[1].lower()#Παίρνουμε τον 1 χαρακτήρα μετά το @ για να ελέγξουμε αν το domain είναι στη λίστα των επιτρεπτών domains
                                                    #email = name@domain.com ,κανει split στο @ και εχουμε [name , domain] = [0, 1] ,άρα το [1]=domain.com ή .gr κλπ.,το οποίο το μετατρέπω σε πεζά 
                if domain not in allowed_domains:
                    self.email_error.setText("• Λάθος email domain.")
                    self.email_error.show()
                    self.email_input.setStyleSheet(input_style_register_window() + "border: 1px solid #E74C3C;")
                    valid = False

                if not email.endswith((".com", ".gr", ".net", ".org")):
                    self.email_error.setText("• Το email πρέπει να καταλήγει σε .com, .gr, \n .net ή .org")
                    self.email_error.show()
                    self.email_input.setStyleSheet(input_style_register_window() + "border: 1px solid #E74C3C;")
                    valid = False
           
            if not valid:
                return # Σταματάμε αν υπάρχει σφάλμα


            #Έλεγχος αν το email υπάρχει ήδη στη βάση δεδομένων
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email=?", (email,))
            existing_email = cursor.fetchone()
            
            if existing_email:
                self.email_already_exists_error.setText("• Το email αυτό χρησιμοποιείται ήδη.")
                self.email_already_exists_error.show()
                self.email_input.setStyleSheet(input_style_register_window() + "border: 1px solid #E74C3C;")
                valid = False
                conn.close() #Κλείνουμε τη σύνδεση με τη βάση δεδομένων πριν επιστρέψουμε,για να μην έχουμε ανοιχτές συνδέσεις που δεν χρησιμοποιούνται
                return # Σταματάμε αν υπάρχει σφάλμα,σταματάει η διαδικασία εγγραφής αν το email υπάρχει ήδη 
            
            #Έλεγχος αν το Όνοματεπώνυμο υπάρχει ήδη στη βάση δεδομένων
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username=?", (name,))
            existing_name = cursor.fetchone()
            
            if existing_name:
                self.name_already_exists_error.setText("• Αυτό το όνομα χρήστη χρησιμοποιείται ήδη.")
                self.name_already_exists_error.show()
                self.name_input.setStyleSheet(input_style_register_window() + "border: 1px solid #E74C3C;")
                valid = False
                conn.close() 
                return 
            
            #Έλεγχος αν το password υπάρχει ήδη στη βάση δεδομένων
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE password=?", (password,))
            existing_password = cursor.fetchone()
            
            if existing_password:
                self.password_already_exists_error.setText("• Αυτό το συνθηματικό χρησιμοποιείται ήδη.")
                self.password_already_exists_error.show()
                self.password_input.setStyleSheet(input_style_register_window() + "border: 1px solid #E74C3C;")
                valid = False
                conn.close() 
                return

                                     
            try:
                cursor.execute("INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)",
                            (name, email, password, selected_role))
                conn.commit()
                QMessageBox.information(self, "Εγγραφή", "Επιτυχής εγγραφή! Συνδέσου τώρα.")
                self.role = selected_role  # Θέσε τον ρόλο ώστε να γίνει login με τον σωστό ρόλο
                self.host.load_login_fields(prefill_email=email, prefill_password=password)  # Προ-γέμισε τα πεδία σύνδεσης με τα στοιχεία που μόλις εγγράφηκαν
            except Exception as e:
                QMessageBox.warning(self, "Σφάλμα", f"Προέκυψε σφάλμα κατά την εγγραφή: {str(e)}")
            finally:
                conn.close()

                                     
            
        
        


        