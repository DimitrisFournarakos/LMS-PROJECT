from PyQt5.QtWidgets import QGraphicsDropShadowEffect
from PyQt5.QtGui import QColor

def get_main_window_style():
    """Επιστρέφει το γενικό στυλ για τα παράθυρα της εφαρμογής."""
    return """
        QWidget {
            font-family: 'Segoe UI';
            font-size: 18px;
        }
        QPushButton {
            padding: 10px;
            background-color: #f5deb3; /* Wheat (Μπεζ) αντί για μπλε */
            color: #5d4037;            /* Σκούρο καφέ για αντίθεση */
            border: 1px solid #d2b48c;
            border-radius: 8px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #c2b280; /* Το μπεζ του header */
            color: white;
        }
        QLineEdit {
            padding: 8px;
            border: 1px solid #aaa;
            border-radius: 6px;
            background-color: #fff8e7; /* Cosmic Latte (πολύ ανοιχτό μπεζ) */
        }
    """

def get_table_header_style():
    return """
        /* Αυτό βάφει όλη τη γραμμή του header μέχρι το τέρμα δεξιά */
        QHeaderView {
            background-color: #c2b280;
            border: none;
        }
        QHeaderView::section {
            background-color: #c2b280;
            color: white;
            padding: 6px;
            border: 1px solid #a8996b;
            font-weight: bold;
        }
    """

def get_table_widget_style():
    """Στυλ πίνακα που δένει με το μπεζ θέμα."""
    return """
        QTableWidget {
            background-color: rgba(255, 250, 240, 0.5); /* Floral White ημιδιαφάνεια */
            alternate-background-color: rgba(245, 222, 179, 0.3); /* Ελαφρύ Wheat στα rows */
            border: 1px solid #c2b280;
            border-radius: 8px;
            gridline-color: rgba(194, 178, 128, 0.3);
            color: #3e2723;
            selection-background-color: #c2b280;
            selection-color: white;
        }
        
        /* Κουμπί 'Προβολή/Διαλέξεις' μέσα στον πίνακα */
        QTableWidget QPushButton {
            background-color: #5d4037; /* Σκούρο καφέ/μπρούτζινο για να ξεχωρίζει */
            color: #fff8e7;
            border: none;
            border-radius: 4px;
            padding: 4px 8px;
            font-weight: bold;
            font-size: 14px;
            margin: 2px;
        }
        
        QTableWidget QPushButton:hover {
            background-color: #8d6e63;
        }

        /* Hover effect στα κελιά που ταιριάζει με το μπεζ */
        QTableWidget::item:hover {
            background-color: rgba(255, 253, 208, 0.8); /* Cream χρώμα */
            color: #5d4037;
        }
        
    """


def get_table_wrapper_style():
    """Το εξωτερικό πλαίσιο που αγκαλιάζει τον πίνακα."""
    return """
        background-color: rgba(255, 255, 255, 150); 
        border: 1px solid rgba(194, 178, 128, 0.4);
        border-radius: 10px;
    """

def get_right_panel_container_style():
    """Στυλ για το δεξί panel διαχείρισης."""
    return """
        background-color: #e0e0e0;
        border-radius: 12px;
        padding: 18px;
        border: 1px solid #bbb;
    """

def subjects_list_style():
    """Στυλ για τον τίτλο Λίστα Μαθημάτων"""
    return """
        font-size: 24px; 
        font-weight: bold; 
        color: #0d47a1; 
        letter-spacing: 1px;
        font-family: 'Segoe UI', sans-serif;
        """

def apply_shadow(widget,blur=8,x=2,y=2,alpha=50):
    """Εφαρμόζει σκιά σε ένα widget"""
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(blur)
    shadow.setXOffset(x)
    shadow.setYOffset(y)
    shadow.setColor(QColor(255, 255, 255, alpha))
    widget.setGraphicsEffect(shadow)

def title_frame_style():
    return"""
    #TitleFrame {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #e3f2fd, stop:1 white);
        border-left: 5px solid #0d47a1;
        border-radius: 5px;
        padding: 5px;
                }
        """

# Αριστερή πλευρά - branding panel
def main_window_left_side():
    return """
            QFrame {
                border-top-left-radius: 30px;
                border-bottom-left-radius: 30px;
                border-top-right-radius: 0px;
                border-bottom-right-radius: 0px;
                border: none;
                background-color: transparent;
                
                
            }
        """
def main_window_left_side_rounded_label():
    return """
                    QLabel {
                        border-top-left-radius: 30px;
                        border-bottom-left-radius: 30px;
                    }
                """

def main_window_right_side_login():
    return """
            QFrame {
                background-color: rgba(30, 60, 90, 180); /* Ένα βαθύ, απαλό ημιδιαφανές μπλε */
                border: 1px solid rgba(255, 255, 255, 0.2); /* Λεπτό λευκό περίγραμμα για εφέ γυαλιού */
                border-radius: 12px;
            }
        """
def main_window_exit_button():
    return """
            QPushButton {
                background-color: transparent;
                color: #2E86C1;
                font-weight: bold;
                border: none;
                padding: 10px;
            }
            QPushButton:hover {
                color: red;
            }
        """

def input_style_login_window():
    return """
        QLineEdit {
            padding-left: 7px;
            padding-right: 7px;
            font-size: 18px;
            color: #333;
            border: 1px solid #dbdbdb; /* Πολύ απαλό περίγραμμα */
            border-radius: 8px;
            background-color: #f9f9f9; /* Ελαφρώς off-white για να είναι ξεκούραστο */
            min-height: 42px;
        }

        /* Όταν ο χρήστης επιλέγει το πεδίο */
        QLineEdit:focus {
            border: 1px solid #2E86C1;
            background-color: white;
        }

           """

def input_style_register_window(): 
    return """
        QLineEdit, QComboBox {
            padding-left: 7px;
            padding-right: 7px;
            font-size: 18px;
            color: #333;
            border: 1px solid #dbdbdb; /* Πολύ απαλό περίγραμμα */
            border-radius: 8px;
            background-color: #f9f9f9; /* Ελαφρώς off-white για να είναι ξεκούραστο */
            min-height: 42px;
        }

        /* Όταν ο χρήστης επιλέγει το πεδίο */
        QLineEdit:focus, QComboBox:focus {
            border: 1px solid #2E86C1;
            background-color: white;
        }
    """
def input_style_role_combo_register():
    return """
        QComboBox{
         padding-left: 15px;
            padding-right: 15px;
            font-size: 14px;
            color: #333;
            border: 1px solid #dbdbdb; /* Πολύ απαλό περίγραμμα */
            border-radius: 8px;
            background-color: #f9f9f9; /* Ελαφρώς off-white για να είναι ξεκούραστο */
            min-height: 37px;
        }
        /* Όταν ο χρήστης επιλέγει το πεδίο */
        QComboBox:focus {
            border: 1px solid #2E86C1;
            background-color: white;
        }
        QComboBox::down-arrow:hover {
            border-top-color: #2E86C1; /* Γίνεται μπλε στο hover */
        }

        /* Minimal στυλ για το ComboBox */
        QComboBox::drop-down {
            border: none; /* Αφαιρούμε το χώρισμα */
            width: 30px;
        }
           """

def back_btn_style():
    return """
            QPushButton {
            color: #2E86C1;
            background-color: transparent;
            border: none;
            font-size: 19px;
            font-weight: 600;                                        
                            }
            QPushButton:hover {
            color: #1B4F72;
            text-decoration: none;
                               }
            """

def login_register_window():
    return """
           QPushButton {
           background-color: #2E86C1; 
           color: white; 
           padding-left: 20px; 
           padding-right: 10px;           
           font-size: 19px;
           border-radius: 5px; 
           min-height: 47px;
           border: none;
           
           }
           QPushButton:hover {
           background-color: #3498DB; /* Ένα ελαφρώς πιο ανοιχτό μπλε */
                             }
           QPushButton:pressed {
           background-color: #21618C; /* Πιο σκούρο μπλε όταν πατηθεί */
                               }
           """

def login_register_user_title_style():
    return """
    QLabel {
        color: #2C3E50;
        padding: 15px;
        background-color: rgba(248, 249, 250, 210);
        border-radius: 15px;
        margin-bottom: 20px;
        border: 1px solid #eeeeee; /* Λεπτό περίγραμμα */
    }QFrame {
        background-color: rgba(255, 255, 255, 180); /* 180 είναι η διαφάνεια (0-255) */
        border: 1px solid rgba(255, 255, 255, 100); /* Λευκό διαφανές περίγραμμα */
        border-radius: 30px;
    }

"""

def register_button_white():
    return """
        QPushButton {
            color:#5DADE2;             /* Καθαρό άσπρο */
            background-color: transparent;
            border: none;
            font-size: 16px;
            font-weight: 490;
            text-decoration: none;
            padding: 0px;
            margin-left: 5px;
        }
        QPushButton:hover {
            color: #E0E0E0;             /* Γίνεται ελαφρώς γκρι στο hover για να φαίνεται ότι πατιέται */
            text-decoration: underline; /* Προαιρετικό: υπογράμμιση μόνο στο hover */
        }
    """


def sidebar_style():
    return """
        QFrame {
            background-color: #2c3e50; /* Σκούρο μπλε-γκρι */
            border: none;
            border-right: 1px solid #1a252f; /* Λεπτή διαχωριστική γραμμή */
        }
        
        /* Στυλ για τα κουμπιά μέσα στο Sidebar */
        QPushButton {
            text-align: left;
            padding: 12px 20px;
            border: none;
            background-color: transparent;
            color: #ecf0f1;
            font-size: 14px;
            font-family: 'Segoe UI', sans-serif;
        }

        QPushButton:hover {
            background-color: #34495e;
            border-left: 5px solid #3498db; /* Μπλε "ένδειξη" στα αριστερά στο hover */
            padding-left: 15px; /* Μικρή κίνηση του κειμένου */
        }

        QPushButton:pressed {
            background-color: #1a252f;
        }

        /* Στυλ για τον Τίτλο (QLabel) μέσα στο Sidebar */
        QLabel {
            color: #ffffff;
            font-weight: bold;
            font-size: 16px;
            background-color: transparent;
            border: none;
        }
    """