from window import *


class App(QApplication):
    def __init__(self):
        super().__init__([])

        self.setStyleSheet(
            """
            VideoFeedFrame {
                background: grey;
                background: white;
                border: 1px solid grey;
                border-radius: 4px;
            }
            VideoFeedFrame QLabel {
                font-size: 50px;
                color: grey;
                font-weight: bold;
                border-radius: 4px;
            }
            ConfigFrame {
                background: pink;
                background: grey;
                background: white;
                border: 1px solid grey;
                border-radius: 4px;
            }
            ConfigFrame QLabel, ConfigFrame QRadioButton, ConfigFrame QLineEdit, ConfigFrame QComboBox {
                border: 1px solid white;
                border-radius: 4px;
                font-size: 15px;
                padding: 5px;
            }
            ConfigFrame QLabel {
                border: none;
                font-size: 14px;
                font-weight: bold;
            }
            ConfigFrame QLineEdit {
                border: 1px solid grey;
                font-size: 13px;
                font-weight: bold;
                padding: 3px;
            }
            ConfigFrame QPushButton {
                border: 1px solid white;
                color: white;
                background: grey;
                font-size: 14px;
                font-weight: bold;
                border-radius: 10px;
                padding: 8px;
            }
            ConfigFrame QPushButton:hover {
                background: lightgrey;
            }
            ConfigFrame QPushButton#toggleVideoButton:checked {
                background: red;
            }
            ConfigFrame QPushButton:pressed {
                background: deepgrey;
            }
            ConfigFrame QComboBox {
                border: 1px solid grey;
            }
            ConfigFrame QComboBox::indicator {
                border: 1px solid grey;
            }
            ConfigFrame  QComboBox::drop-down {
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 1px;
                border-left-style: solid;
                border-top-right-radius: 4px;
                border-bottom-right-radius: 4px;
                background-color: lightgray;
            }
            Login QLabel {
                font-size: 30px;
                font-weight: bold;
            }
            Login QLineEdit {
                font-size: 15px;
                font-weight: bold;
            }
        """
        )

        self.window = Window()


app = App()
app.exec()
