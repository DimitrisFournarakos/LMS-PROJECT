from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,QAction,QHBoxLayout
from PyQt5.QtCore import Qt,QSize
from PyQt5.QtGui import QFont,QIcon
from register_window import RegisterWindow,toggle_password_visibility
from styles_css.styles import input_style_login_window,login_register_window,login_register_user_title_style,register_button_white

class LoginWindow(QWidget):
    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.login_layout = QVBoxLayout(self)
        
        self.register_helper = None# Θα κρατήσουμε το RegisterWindow instance ώστε να μην garbage-collected
        self.load_login_fields()
    
    def clear_login_frame(self):#Η clear_login_frame κάνει reset του layout login_layout
        while self.login_layout.count(): #Εκτελεί τον κώδικα όσο υπάρχουν items μέσα στο layout,θα καθαρίσει όλα τα στοιχεία στο layout ένα-ένα
            child = self.login_layout.takeAt(0)#takeAt(0) παίρνει το πρώτο item (στην θέση 0) από το layout και το αφαιρεί από το layout,αλλά δεν το διαγράφει από την μνήμη.
            if child.widget():#Ελέγχει αν το child είναι πραγματικό widget (κάποιο κουμπί, γραμμή κειμένου, label κλπ)
                child.widget().deleteLater()#Αυτό προγραμματίζει το widget να διαγραφεί από τη μνήμη μόλις τελειώσει η τρέχουσα εκτέλεση των events
                                            #Είναι ένας ασφαλής τρόπος να διαγράψεις ένα widget χωρίς να σπάσει η ροή του προγράμματος.

    def load_login_fields(self, prefill_email="", prefill_password=""):
        #Ελέγχουμε αν υπάρχουν τιμές στα πεδία prefill_email και prefill_password, αν όχι, τα ορίζουμε ως κενές συμβολοσειρές.
        #Aν τα πεδία prefill_email και prefill_password είναι τύπου bool (π.χ. False), τότε τα ορίζουμε ως κενές συμβολοσειρές.
        #Γιατί εμείς θέλουμε να περιέχουν strings (email,password) για να μπορέσουμε να τα βάλουμε σε QLineEdit(πεδίο κειμένου)
        #istance() έλεγχος τύπου δεδομένων, αν το prefill_email ή prefill_password είναι boolean (π.χ. False), τότε τα ορίζουμε ως κενές συμβολοσειρές, ώστε να μην προκαλέσουν σφάλματα 
        #Χρησιμοποιείται για ασφαλεια των πεδίων prefill_email,prefill_password όταν περνάμε τα στοιχεία του νέου χρήστη μετά από Επιτυχής Εγγραφή
        if isinstance(prefill_email, bool):
            prefill_email = ""
        if isinstance(prefill_password, bool):
            prefill_password = ""

        self.clear_login_frame()

        title = QLabel(f"Σύνδεση Xρήστη \n")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setStyleSheet(login_register_user_title_style())
        title.setAlignment(Qt.AlignCenter)

        subtitle = QLabel("Απαιτείται <span style='color:red;'>εγγραφή</span> πριν την πρώτη είσοδο.")
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet(login_register_user_title_style())
        subtitle.setFont(QFont("Arial", 10))
        subtitle.setAlignment(Qt.AlignCenter)
             
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        self.email_input.setStyleSheet(input_style_login_window())
        self.email_input.setText(prefill_email)

        # Προσθήκη εικονιδίου Email τέρμα δεξιά
        email_icon = QIcon("icons/email-icon.png")
        self.email_input.addAction(email_icon, QLineEdit.TrailingPosition)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Συνθηματικό (password)")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet(input_style_login_window())
        self.password_input.setText(prefill_password)

        self.password_visible = False
        self.eye_action = QAction(QIcon("icons/eye_close.png"),"", self.password_input)
        self.password_input.addAction(self.eye_action, QLineEdit.TrailingPosition)
        self.eye_action.setToolTip("Εμφάνιση/Απόκρυψη συνθηματικού")
        self.eye_action.triggered.connect(lambda: toggle_password_visibility(self))

        login_btn = QPushButton("Είσοδος ")
        login_btn.setStyleSheet(login_register_window())
        login_btn.setCursor(Qt.PointingHandCursor)
        login_btn.clicked.connect(lambda: self.parent_window.authenticate_user())

        #Προσθήκη εικονιδίου στο κουμπί εισόδου
        login_icon = QIcon("icons/login-icon.png")
        login_btn.setIcon(login_icon)
        login_btn.setIconSize(QSize(20, 20)) # Ορίζεις το μέγεθος του εικονιδίου
        login_btn.setLayoutDirection(Qt.RightToLeft) # Τοποθετεί το εικονίδιο στα δεξιά του κειμένου   
               
        #Μήνυμα σφάλματος σύνδεσης, αρχικά κρυφό
        self.login_error = QLabel("")
        self.login_error.setStyleSheet("color: #E74C3C; font-size: 16px; margin-left: 5px; background: none; border: none;")
        self.login_error.hide() 

        self.login_successful = QLabel("")
        self.login_successful.setStyleSheet("color: #27AE60; font-size: 16px; margin-left: 5px; background: none; border: none;")
        self.login_successful.hide()  
            
        #Δημιουργούμε ένα QWidget που θα κρατάει το layout της εγγραφής
        register_container = QWidget()
        register_layout = QHBoxLayout(register_container) # Σύνδεση layout με το container,δημιουργούμε ένα οριζόντιο layout για να είναι το κείμενο και το κουμπί στην ίδια σειρά
        register_layout.setContentsMargins(0, 0, 0, 0)
        register_layout.setAlignment(Qt.AlignCenter)

        #Τα Widgets που θα προσθέσουμε στο register_layout
        no_account_label = QLabel("Δεν έχετε λογαριασμό;")
        no_account_label.setStyleSheet("color: #D1D1D1; font-size: 15px; border: none; background: transparent;")

        self.register_btn = QPushButton("Εγγραφή")
        self.register_btn.setCursor(Qt.PointingHandCursor)
        self.register_btn.setStyleSheet(register_button_white()) 
        self.register_btn.clicked.connect(self.open_register)

        #Προσθήκη στο layout του container
        register_layout.addWidget(no_account_label)
        register_layout.addWidget(self.register_btn)
     
        # Προσθήκη των widgets στο layout,με την σωστή σειρά και με κενά ανάμεσά τους για καλύτερη εμφάνιση
        self.login_layout.addWidget(title)
        self.login_layout.addWidget(subtitle)
        self.login_layout.addWidget(self.email_input)
        self.login_layout.addSpacing(5)
        self.login_layout.addWidget(self.password_input)
        self.login_layout.addSpacing(20)
        self.login_layout.addWidget(login_btn)
        self.login_layout.setSpacing(8)
        self.login_layout.addWidget(self.login_error)
        self.login_error.setFixedHeight(17) # Δίνω ένα μικρό, σταθερό ύψος,για να μην μικρίνει το qframe απο πάνω
        self.login_error.setAlignment(Qt.AlignCenter)
        self.login_layout.addWidget(self.login_successful)
        self.login_successful.setFixedHeight(17) # Δίνω ένα μικρό, σταθερό ύψος,για να μην μικρίνει το qframe απο πάνω
        self.login_successful.setAlignment(Qt.AlignCenter) 
        
        
        

        self.login_layout.addWidget(register_container)

    def open_register(self):#μετάβαση στο παράθυρο εγγραφής,μόλις καλέσω την συνάρτηση open_register με το κουμπί Εγγραφή,θα ανοίξει το παράθυρο εγγραφής και θα κλείσει το παράθυρο σύνδεσης
        if self.register_helper is None:
            self.register_helper = RegisterWindow(self)
        
        self.register_helper.open_register(self)

    
    