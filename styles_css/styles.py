from PyQt5.QtWidgets import QGraphicsDropShadowEffect, QFrame, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtGui import QColor, QPixmap
from PyQt5.QtCore import Qt

def get_main_window_style():
    """Επιστρέφει το γενικό στυλ για τα παράθυρα της εφαρμογής."""
    return """
        QWidget {
            font-family: 'Noto Sans', 'Segoe UI', Arial, sans-serif;
            font-size: 17px;
        }
        QPushButton {
            padding: 10px;
            background-color: #f5deb3; /* Wheat (Μπεζ) αντί για μπλε */
            color: #5d4037;            /* Σκούρο καφέ για αντίθεση */
            border: 1px solid #d2b48c;
            border-radius: 8px;
            font-weight: 600;
            font-size: 17px;
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
            font-size: 17px;
            font-weight: 500;
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
            font-family: 'Noto Sans', 'Segoe UI', Arial, sans-serif;
            font-size: 17px;
            font-weight: 700;
        }
    """

def get_table_widget_style():
    """Στυλ πίνακα που δένει με το μπεζ θέμα."""
    return """
        QTableWidget {
            font-family: 'Noto Sans', 'Segoe UI', Arial, sans-serif;
            font-size: 17px;
            font-weight: 600;
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

        QTableWidget::item {
            padding: 4px;
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

def student_quiz_main_container_style():
    """Στυλ για το κύριο container της επιλογής quiz"""
    return """
        background-color: #f5f5f5;
    """

def student_quiz_instruction_style():
    """Στυλ για το instruction label της επιλογής quiz"""
    return """
        font-size: 16px;
        color: #34495e;
        font-weight: 500;
    """

def student_quiz_group_style():
    """Στυλ για τα group boxes των μαθημάτων και των quizzes"""
    return """
        QGroupBox {
            border: 2px solid #bdc3c7;
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 10px;
            font-weight: bold;
            color: #2c3e50;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 3px 0 3px;
        }
    """

def student_quiz_list_style():
    """Στυλ για τις λίστες μαθημάτων και quizzes"""
    return """
        QListWidget {
            border: 1px solid #ddd;
            border-radius: 6px;
            background-color: white;
            padding: 5px;
        }
        QListWidget::item {
            padding: 10px;
            margin: 2px 0px;
            border-radius: 4px;
            background-color: #ecf0f1;
            color: #2c3e50;
            font-size: 14px;
        }
        QListWidget::item:hover {
            background-color: #d5dbdb;
            color: #1a252f;
        }
        QListWidget::item:selected {
            background-color: #3498db;
            color: white;
            font-weight: bold;
        }
    """

def student_quiz_button_style(color):
    """Στυλ για τα action buttons της επιλογής quiz"""
    def _adjust_color(hex_color, factor):
        hex_color = hex_color.lstrip('#')
        r, g, b = [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]
        r = max(0, min(255, int(r * factor)))
        g = max(0, min(255, int(g * factor)))
        b = max(0, min(255, int(b * factor)))
        return f'#{r:02x}{g:02x}{b:02x}'

    hover_color = _adjust_color(color, 1.2)
    pressed_color = _adjust_color(color, 0.85)
    return f"""
        QPushButton {{
            background-color: {color};
            color: white;
            border: none;
            border-radius: 6px;
            padding: 10px 20px;
            font-size: 14px;
            font-weight: bold;
            cursor: pointer;
        }}
        QPushButton:hover {{
            background-color: {hover_color};
        }}
        QPushButton:pressed {{
            background-color: {pressed_color};
        }}
    """

def apply_shadow(widget,blur=8,x=2,y=2,alpha=50):
    """Εφαρμόζει σκιά σε ένα widget"""
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(blur)
    shadow.setXOffset(x)
    shadow.setYOffset(y)
    shadow.setColor(QColor(255, 255, 255, alpha))
    widget.setGraphicsEffect(shadow)

def window_title_frame_style(title_text, subtitle_text=None, icon_path=None):
    header_frame = QFrame()
    header_frame.setObjectName("LeaderboardTitleFrame")
    header_frame.setStyleSheet(leaderboard_title_style())

    header_layout = QVBoxLayout(header_frame)
    header_layout.setContentsMargins(18, 14, 18, 14)
    header_layout.setSpacing(4)

    title_row = QHBoxLayout()
    title_row.setSpacing(10)
    title_row.setContentsMargins(0, 0, 0, 0)

    if icon_path:
        icon_label = QLabel()
        icon_pixmap = QPixmap(icon_path)
        if not icon_pixmap.isNull():
            icon_label.setPixmap(icon_pixmap.scaled(28, 28, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        icon_label.setFixedSize(28, 28)
        icon_label.setAlignment(Qt.AlignVCenter)
        title_row.addWidget(icon_label)

    title_label = QLabel(title_text)
    title_label.setObjectName("LeaderboardTitleMain")
    title_row.addWidget(title_label)
    title_row.addStretch()

    header_layout.addLayout(title_row)

    if subtitle_text:
        subtitle_label = QLabel(subtitle_text)
        subtitle_label.setObjectName("LeaderboardTitleSub")
        subtitle_label.setWordWrap(True)
        header_layout.addWidget(subtitle_label)

    return header_frame

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

def students_stats_rounded_container():
    return """   
            QFrame {
                background-color: white;
                border-radius: 20px;               
            }       
    """

def students_stats_rounded_sub_list():
    return """
            QListWidget {
                background: transparent;
                font-size: 14px;
                border: None;
                padding: 5px;
            }
            /* Το κυρίως σώμα του Scrollbar */
            QScrollBar:vertical {
                border: none;
                background: #f1f2f6; /* Πολύ απαλό γκρι/μπλε φόντο */
                width: 10px;         /* Πιο λεπτό και κομψό */
                margin: 0px 0px 0px 0px;
                border-radius: 5px;
            }
            /* Η "λαβή" (το μέρος που σέρνει ο χρήστης) */
            QScrollBar::handle:vertical {
                background: #dcdde1; /* απαλό γκρι  */
                min-height: 20px;
                border-radius: 5px;
            }
            /* Χρώμα όταν ο χρήστης περνάει το ποντίκι από πάνω (hover) */
            QScrollBar::handle:vertical:hover {
                background: #ced6e0; /* Ένα λιγο ανοιχτό μπλε/γκρι για feedback */
            }
            /* Αφαιρούμε τα κλασικά βελάκια πάνω και κάτω για πιο clean look */
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """

def available_courses_list_style():
    return """          
    QListWidget {
        background-color: #ffffff;
        border: 2px solid #dcdde1;
        border-radius: 10px;
        padding: 10px;
        font-family: 'Segoe UI', sans-serif;
        font-size: 16px;
        color: #2f3640;
    }
    
    QListWidget::item {
        padding: 12px;
        border-bottom: 1px solid #f1f2f6;
        font-weight: 500;
    }

    QListWidget::item:selected {
        background-color: #E0E0E0;
        color: black;
        border-radius: 5px;
    }
        """

def subjects_available_course_list_style():
    """
    QListWidget {
        background-color: #ffffff;
        border: 2px solid #dcdde1;
        border-radius: 12px;
        outline: none; /* Βγάζει τις τελείες/κύκλους εστίασης */
        padding: 5px;
    }
    
    QListWidget::item {
        background-color: transparent;
        border-bottom: 1px solid #f1f2f6;
        margin-bottom: 2px;
        border-radius: 8px; /* Για να φαίνεται ωραία το hover */
    }

    /* Hover effect σε όλη τη σειρά */
    QListWidget::item:hover {
        background-color: #f8f9fa; /* Πολύ απαλό γκρι */
        border-bottom: 1px solid #dcdde1;
    }

    /* Απενεργοποίηση του κλασικού μπλε/γκρι selection */
    QListWidget::item:selected {
        background-color: #f1f2f6; 
        color: #2f3640;
        border: none;
        outline: none;
    }
"""

def subjects_available_back_btn_style():
    return """
                QPushButton { 
                    background-color: #dddec8; 
                    border-radius: 12px; /*Στρογγύλεμμα περιγράμματος κουμπιού*/
                    border: none;
                }
                QPushButton:hover { 
                    background-color: #ecece2; /* Γίνεται γκριζο-μπεζ στο hover */
                    border: 1px solid #959595; /* Μικρή σκιά για βάθος */
                }
                QPushButton:pressed {
                    padding-top: 2px; /* Εφέ πίεσης */
                }
            """

def lecture_btn_style():
    return """
    QPushButton {
        border: none;
        background-color: transparent;
        color: #555555; /* Γκρι για ηρεμία */
        padding: 5px;
        font-size: 16px;
    }
    QPushButton:hover {
        color: #2c3e50; /* Το χρώμα της μπάρας σου */
        background-color: #f0f2f5; /* Ελαφρύ γκρι φόντο στο hover */
        border-radius: 4px;
    }
          """

def unenroll_btn_style():
    return  """
    QPushButton {
        border: none;
        background-color: transparent;
        color: #555555;
        padding: 5px;
        font-size: 16px;
    }
    QPushButton:hover {
        color: #e74c3c; /* Μαλακό κόκκινο */
        background-color: #fdeaea; /* Πολύ απαλό κόκκινο φόντο */
        border-radius: 4px;
    }
           """

def lectures_back_btn_style():
    return """
            QPushButton {
                border: none;
                background: transparent;
            }
            QPushButton:hover {
                background-color: rgba(220, 53, 69, 0.15);
                border-radius: 4px;
            }
            QPushButton:pressed {
                background-color: rgba(220, 53, 69, 0.3);
            }
        """

def lectures_prev_page_btn_style():
    return """
            QPushButton {
                border: none;
                background: transparent;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: rgba(52, 152, 219, 0.15);
            }
            QPushButton:pressed {
                background-color: rgba(52, 152, 219, 0.3);
            }
            QPushButton:disabled {
                opacity: 0.5;
            }
        """

def lectures_next_page_btn_style():
    return """
            QPushButton {
                border: none;
                background: transparent;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: rgba(52, 152, 219, 0.15);
            }
            QPushButton:pressed {
                background-color: rgba(52, 152, 219, 0.3);
            }
            QPushButton:disabled {
                opacity: 0.5;
            }
        """

def leaderboard_student_style():
    return """
        QTableWidget {
            border: 1px solid #34495e;
            border-radius: 6px;
            padding: 0px;
            margin: 0px;
            font-size: 14px;
            font-weight: 500;
            background: #f8f9fa;
            alternate-background-color: #ecf0f1;
            gridline-color: #bdc3c7;
            color: #2c3e50;
            selection-background-color: #3498db;
            selection-color: white;
            outline: 0;
        }

        QTableWidget QHeaderView {
            border: none;
            margin: 0px;
            padding: 0px;
            background: #eef2f5;
        }
        
        QTableWidget QHeaderView::section:horizontal {
            background-color: #eef2f5;
            color: #1f2d3a;
            font-weight: 600;
            font-size: 16px;
            font-family: 'Noto Sans', 'Segoe UI', Arial, sans-serif;
            border: none;
            border-bottom: 1px solid #bdc3c7;
            padding: 2px 8px;
            min-height: 52px; /*Βάζω το ύψος των πεδίων των headers*/
        }

        QTableWidget::item {
            padding: 4px 8px;
            border: none;
        }

        QTableCornerButton::section {
            background: transparent;
            border: none;
        }
        
        QTableWidget::item:hover {
            background-color: #d5dbdb;
            color: #2c3e50;
        }
        
        QTableWidget QHeaderView::section:horizontal:hover {
            background-color: #e3e9ee;
            color: #1f2d3a;
            font-weight: 700;
        }

        QTableWidget QScrollBar:vertical {
            border: none;
            background: #f1f2f6;
            width: 10px;
            margin: 0px;
        }

        QTableWidget QScrollBar::handle:vertical {
            background: #cdd3d9;
            min-height: 24px;
            border-radius: 5px;
        }

        QTableWidget QScrollBar::handle:vertical:hover {
            background: #bcc4cc;
        }

        QTableWidget QScrollBar::add-line:vertical,
        QTableWidget QScrollBar::sub-line:vertical {
            height: 8px;
            width: 10px;
            border: none;
            background: #eef2f5;
        }

        QTableWidget QScrollBar::up-arrow:vertical,
        QTableWidget QScrollBar::down-arrow:vertical {
            width: 25px;
            height: 25px;
            background: #7a8794;
        }

        QTableWidget QScrollBar::add-page:vertical,
        QTableWidget QScrollBar::sub-page:vertical {
            background: transparent;
        }
    """


def leaderboard_scroll_style():
    return """
        QGroupBox {
            border: 1px solid #d9e1e8;
            border-radius: 12px;
            margin-top: 14px;
            background: white;
            font-size: 18px;
            font-weight: 700;
            color: #2c3e50;
        }

        QGroupBox::title {
            subcontrol-origin: margin;
            left: 14px;
            padding: 0 8px;
        }

        QGroupBox#LeaderboardItemGroup {
            border: 1px solid #d9e1e8;
            border-radius: 10px;
            margin-top: 10px;
            background: #f8fbfd;
            font-weight: 600;
            color: #1f2d3a;
        }

        QGroupBox#LeaderboardItemGroup::title {
            subcontrol-origin: margin;
            left: 12px;
            padding: 0 6px;
        }

        QScrollArea {
            border: none;
            background: transparent;
        }

        QScrollArea QWidget#LeaderboardContent {
            background: transparent;
        }

        QScrollBar:vertical {
            border: none;
            background: #f1f2f6;
            width: 16px; /* Κάνω το scrollbar λίγο πιο φαρδύ για καλύτερη αίσθηση και χρήση */
            margin: 6px 2px 6px 6px; /*βάζω περιθώριο για να μην κολλάει το scrollbar στο περιθώριο του groupbox*/
            border-radius: 6px;
        }

        QScrollBar::handle:vertical {
            background: #cdd3d9;
            min-height: 30px;
            border-radius: 6px;
        }

        QScrollBar::handle:vertical:hover {
            background: #bcc4cc;
        }

        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {
            height: 0px;
            width: 0px;
            border: none;
            background: transparent;
        }

        QScrollBar::up-arrow:vertical,
        QScrollBar::down-arrow:vertical {
            width: 0px;
            height: 0px;
            background: transparent;
        }

        QScrollBar::add-page:vertical,
        QScrollBar::sub-page:vertical {
            background: transparent;
        }
    """


def leaderboard_title_style():
    return """
        QFrame#LeaderboardTitleFrame {
            border: 1px solid #d6dee5;
            border-left: 6px solid #6aa6c9;
            border-radius: 14px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #f8fcff, stop:1 #eef4f8);
        }

        QLabel#LeaderboardTitleMain {
            color: #1f2d3a;
            font-size: 22px;
            font-weight: 800;
            letter-spacing: 0.2px;
        }

        QLabel#LeaderboardTitleSub {
            color: #60717f;
            font-size: 14px;
            font-weight: 500;
        }
    """