"""
Enhanced SpinBox - Regular spinboxes with larger, easier-to-click arrows
"""
from PyQt5.QtWidgets import QSpinBox, QDoubleSpinBox

class EnhancedSpinBox(QSpinBox):
    """SpinBox with larger up/down arrows for easier clicking"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Style with larger arrows
        self.setStyleSheet("""
            QSpinBox {
                padding-right: 30px;
            }
            QSpinBox::up-button {
                width: 30px;
                height: 14px;
            }
            QSpinBox::down-button {
                width: 30px;
                height: 14px;
            }
            QSpinBox::up-arrow {
                width: 12px;
                height: 12px;
            }
            QSpinBox::down-arrow {
                width: 12px;
                height: 12px;
            }
        """)


class EnhancedDoubleSpinBox(QDoubleSpinBox):
    """DoubleSpinBox with larger up/down arrows for easier clicking"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Style with larger arrows
        self.setStyleSheet("""
            QDoubleSpinBox {
                padding-right: 30px;
            }
            QDoubleSpinBox::up-button {
                width: 30px;
                height: 14px;
            }
            QDoubleSpinBox::down-button {
                width: 30px;
                height: 14px;
            }
            QDoubleSpinBox::up-arrow {
                width: 12px;
                height: 12px;
            }
            QDoubleSpinBox::down-arrow {
                width: 12px;
                height: 12px;
            }
        """)
