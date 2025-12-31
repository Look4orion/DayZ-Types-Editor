"""
Toggle Switch Widget - iOS-style slider toggle
"""
from PyQt5.QtWidgets import QCheckBox
from PyQt5.QtCore import Qt, QPropertyAnimation, QRectF, pyqtProperty
from PyQt5.QtGui import QPainter, QColor, QPen, QMouseEvent

class ToggleSwitch(QCheckBox):
    """iOS-style toggle switch widget"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(50, 24)
        self._position = 0
        self.animation = QPropertyAnimation(self, b"position")
        self.animation.setDuration(100)
        self.stateChanged.connect(self.on_state_changed)
    
    @pyqtProperty(int)
    def position(self):
        return self._position
    
    @position.setter
    def position(self, pos):
        self._position = pos
        self.update()
    
    def on_state_changed(self, state):
        self.animation.stop()
        if state == Qt.Checked:
            self.animation.setStartValue(self._position)
            self.animation.setEndValue(26)
        else:
            self.animation.setStartValue(self._position)
            self.animation.setEndValue(0)
        self.animation.start()
    
    def mousePressEvent(self, event):
        """Handle mouse click to toggle"""
        if event.button() == Qt.LeftButton:
            self.toggle()  # Toggle the checkbox state
        super().mousePressEvent(event)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw track
        if self.isChecked():
            track_color = QColor("#0e639c")  # Blue when ON
        else:
            track_color = QColor("#555")  # Gray when OFF
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(track_color)
        painter.drawRoundedRect(0, 0, 50, 24, 12, 12)
        
        # Draw thumb (slider circle)
        thumb_color = QColor("#ffffff")
        painter.setBrush(thumb_color)
        painter.drawEllipse(self._position, 2, 20, 20)
        
        # Draw text
        painter.setPen(QPen(QColor("#ffffff")))
        if self.isChecked():
            painter.drawText(5, 16, "ON")
        else:
            painter.drawText(28, 16, "OFF")
