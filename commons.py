import os
from typing import List

# try:
#     from PySide6.QtGui import *
#     from PySide6.QtCore import *
#     from PySide6.QtWidgets import *
# except:
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

Signal = pyqtSignal


class VLine(QFrame):
    def __init__(self):
        super().__init__(self)
        self.setFrameShape(self.Shape.VLine)


class HLine(QFrame):
    def __init__(self):
        super().__init__(self)
        self.setFrameShape(self.Shape.HLine)


class Frame(QFrame):
    LAY = QBoxLayout

    def __init__(self, name: str = ""):
        super().__init__()

        if name:
            self.setObjectName(name)

        self.LAY(self)

    def layout(self) -> QBoxLayout:
        return super().layout()

    def addWidget(self, widget: QWidget, *args):
        self.layout().addWidget(widget, *args)

    def addLayout(self, layout: QLayout, *args):
        self.layout().addLayout(layout, *args)

    def setSpacing(self, spacing: int):
        self.layout().setSpacing(spacing)

    def addSpacing(self, spacing: int):
        self.layout().addSpacing(spacing)

    def addLayout(self, layout: QLayout, *args):
        self.layout().addLayout(layout, *args)

    def addStretch(self):
        self.layout().addStretch()


class VFrame(Frame):
    LAY = QVBoxLayout

    def addHLine(
        self,
        left: int = 0,
        right: int = 0,
        same: bool = True,
    ):
        if same and not (left and right):
            right = left
            left = right
        self.addSpacing(left)
        self.addWidget(HLine())
        self.addSpacing(right)


class HFrame(Frame):
    LAY = QHBoxLayout

    def addVLine(
        self,
        left: int = 0,
        right: int = 0,
        same: bool = True,
    ):
        if same and not (left and right):
            right = left
            left = right
        self.addSpacing(left)
        self.addWidget(VLine())
        self.addSpacing(right)


class GridLayout(QGridLayout):
    def noMargin(self):
        self.setContentsMargins(0, 0, 0, 0)

    def populate(
        self,
        widgets: List[QWidget],
        columns: int = 2,
        spacing: int = 10,
    ):
        if spacing:
            self.setSpacing(10)

        row = column = 0
        for index, widget in enumerate(widgets):
            column = index % columns

            self.addWidget(widget, row, column)

            if index and column == columns - 1:
                row += 1


if __name__ == "__main__":
    os.system("python app.py")
