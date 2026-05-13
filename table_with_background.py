"""
Custom QTableWidget με blur background εφέ.
Χρησιμοποιείται για τη δημιουργία πινάκων με θολωμένο φόντο.
"""

from PyQt5.QtWidgets import QTableWidget, QGraphicsScene, QGraphicsPixmapItem, QGraphicsBlurEffect
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPixmap, QPainter, QImage


class TableWithBackground(QTableWidget):
    """Πίνακας με θολωμένη εικόνα ως background"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bg_pixmap = QPixmap('icons/e-learning.png')
        self.scaled_pixmap = QPixmap()
        self.blur_radius = 8  # Βαθμός του blur
        self.verticalHeader().setVisible(False)  # Κρύβουμε τους αριθμούς αριστερά

    def _blur_pixmap(self, pixmap):
        """Εφαρμόζει blur εφέ σε ένα pixmap χρησιμοποιώντας QGraphicsScene"""
        if pixmap.isNull() or self.blur_radius <= 0:
            return pixmap

        scene = QGraphicsScene()
        item = QGraphicsPixmapItem(pixmap)
        blur_effect = QGraphicsBlurEffect()
        blur_effect.setBlurRadius(self.blur_radius)
        item.setGraphicsEffect(blur_effect)
        scene.addItem(item)

        # Δημιουργούμε QImage για να ζωγραφίσουμε το θολωμένο αποτέλεσμα
        result = QImage(pixmap.size(), QImage.Format_ARGB32_Premultiplied)
        result.fill(Qt.transparent)
        painter = QPainter(result)
        scene.render(painter, QRectF(result.rect()), QRectF(0, 0, pixmap.width(), pixmap.height()))
        painter.end()

        return QPixmap.fromImage(result)

    def resizeEvent(self, event):
        """Ανανεώνει το θολωμένο φόντο όταν αλλάζει το μέγεθος του πίνακα"""
        super().resizeEvent(event)
        if not self.bg_pixmap.isNull():
            w = self.viewport().width()
            h = self.viewport().height()
            scaled = self.bg_pixmap.scaled(w, h, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            self.scaled_pixmap = self._blur_pixmap(scaled)
        self.viewport().update()

    def paintEvent(self, event):
        """Ζωγραφίζει το θολωμένο φόντο πίσω από τα δεδομένα του πίνακα"""
        painter = QPainter(self.viewport())
        if hasattr(self, 'scaled_pixmap') and self.scaled_pixmap:
            # Κεντράρισμα της εικόνας
            x = (self.viewport().width() - self.scaled_pixmap.width()) // 2
            y = (self.viewport().height() - self.scaled_pixmap.height()) // 2
            painter.drawPixmap(x, y, self.scaled_pixmap)
        super().paintEvent(event)
