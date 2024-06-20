import requests, threading
from video import *
from spinner import PRMP_QSpinner
import datetime, json

MODELS = "models"
MODELS = "models"
SNAPSHOTS = "snapshots"
COORDS = "./coords.json"

try:
    os.mkdir(MODELS)
    os.mkdir(SNAPSHOTS)
except:
    ...

RACKS = {}

try:
    with open(COORDS) as file:
        racks = json.load(file)
        if isinstance(racks, dict):
            RACKS = racks
except Exception as e:
    print(e)
    ...


class ConfigFrame(VFrame):
    def __init__(self, win: "VideoNConfig", _):
        super().__init__()

        self.win = win
        self._ = _
        self.win.videoFeedFrame.started.connect(self.onVideoStarted)
        self.win.videoFeedFrame.stopped.connect(self.onVideoStopped)

        self.setFixedHeight(100)

        topHLay = QHBoxLayout()
        self.addLayout(topHLay)

        topHLay.addWidget(QLabel("Video Feed Source : "))

        self.cameraRadio = QRadioButton("Camera")
        topHLay.addWidget(self.cameraRadio)

        self.rtspRadio = QRadioButton("RTSP")
        topHLay.addWidget(self.rtspRadio)

        topHLay.addStretch()

        self.rtspLineEdit = QLineEdit(
            RACKS[self._].get("rtspLink", "")
            # "rtsp://admin:1313Risco@@156.67.21.177:5554/cam/realmonitor?channel=1&subtype=1"
        )
        # self.rtspLineEdit.setMinimumSize(800, 35)
        self.rtspLineEdit.setVisible(False)
        self.rtspLineEdit.setPlaceholderText("Enter RTSP link ...")
        self.rtspLineEdit.returnPressed.connect(self.onToggleVideoButton)
        topHLay.addWidget(self.rtspLineEdit, 1)

        self.rtspRadio.toggled.connect(self.rtspLineEdit.setVisible)
        self.rtspRadio.toggle()

        bottomHLay = QHBoxLayout()
        self.addLayout(bottomHLay)

        bottomHLay.addWidget(QLabel("Select Model : "))

        self.model = ""

        self.modelCombox = QComboBox()
        self.fillModels()

        self.modelCombox.currentTextChanged.connect(self.onModelChanged)

        bottomHLay.addWidget(self.modelCombox)

        bottomHLay.addSpacing(30)

        bottomHLay.addWidget(QLabel("Confidence: "))

        self.confBar = QSlider(Qt.Horizontal)
        self.confBar.setTickInterval(1)
        self.confBar.setRange(0, 10)
        bottomHLay.addWidget(self.confBar)

        self.confLabel = QLabel()
        bottomHLay.addWidget(self.confLabel)

        self.confBar.valueChanged.connect(self.onConfChanged)
        self.confBar.setSliderPosition(RACKS[_].get("conf", 0))

        bottomHLay.addStretch()

        clearRackPositions = QPushButton("Clear Rack Positions")
        clearRackPositions.clicked.connect(self.onClearRackPositions)
        bottomHLay.addWidget(clearRackPositions)

        bottomHLay.addStretch()

        self.toggleVideoButton = QPushButton("Start")
        self.toggleVideoButton.setObjectName("toggleVideoButton")
        self.toggleVideoButton.setCheckable(True)
        self.toggleVideoButton.toggled.connect(self.onToggleVideoButton)
        bottomHLay.addWidget(self.toggleVideoButton)

        takeSnapShot = QPushButton("Take Snapshot")
        takeSnapShot.clicked.connect(self.onTakeSnapShot)
        bottomHLay.addWidget(takeSnapShot)

        bottomHLay.addSpacing(40)

        add = QPushButton("Add Feed")
        add.clicked.connect(self.onAddFeed)
        bottomHLay.addWidget(add)

    def fillModels(self):
        models = [a for a in os.listdir(MODELS) if a.endswith(".engine")]
        self.modelCombox.clear()
        self.modelCombox.addItems(models)

        model = RACKS[self._].get("model", "")
        if model and model in models:
            self.modelCombox.setCurrentText(model)
        else:
            self.onModelChanged("")

    def onAddFeed(self):
        self.window().addFeed()

    def onConfChanged(self, value: int):
        v = value / self.confBar.maximum()
        if self.win.videoFeedFrame.videoThread:
            self.win.videoFeedFrame.videoThread.conf = v

        self.confLabel.setText(str(v))

        RACKS[self._].update(conf=value)
        self.win.videoFeedFrame.videoLabel.saveCoordinates()

    def onModelChanged(self, model: str):
        if model != self.model:
            self.model = model
            RACKS[self._].update(model=model)
            self.win.videoFeedFrame.videoLabel.saveCoordinates()

    def onToggleVideoButton(self, toggled: bool):
        self.toggleVideoButton.setText("Stop" if toggled else "Start")

        if toggled:
            rtspLink = self.rtspLineEdit.text()
            if self.cameraRadio.isChecked():
                rtspLink = 0
            elif not rtspLink:
                return QMessageBox.warning(
                    self,
                    "Invalid RTSP",
                    "Enter a RTSP link.",
                )
            else:
                RACKS[self._].update(rtspLink=rtspLink)
                self.win.videoFeedFrame.videoLabel.saveCoordinates()

            if self.model:
                model = os.path.join(os.path.abspath(MODELS), self.model)

                self.win.videoFeedFrame.startVideoThread(rtspLink, model)
            else:
                return QMessageBox.warning(
                    self,
                    "Invalid Model",
                    "Select a model first.",
                )
        else:
            self.win.videoFeedFrame.stopVideoThread()

    def onVideoStarted(self):
        self.cameraRadio.setDisabled(True)
        self.rtspRadio.setDisabled(True)
        self.rtspLineEdit.setDisabled(True)
        self.modelCombox.setDisabled(True)

    def onClearRackPositions(self):
        self.win.videoFeedFrame.videoLabel.racks.clear()
        self.win.videoFeedFrame.videoLabel.saveCoordinates()
        self.win.videoFeedFrame.videoLabel.update()

    def onVideoStopped(self):
        self.cameraRadio.setEnabled(True)
        self.rtspRadio.setEnabled(True)
        self.rtspLineEdit.setEnabled(True)
        self.modelCombox.setEnabled(True)

    def onTakeSnapShot(self):
        image = self.win.videoFeedFrame.image
        if image:
            file = f"snapshot-{datetime.datetime.now()}"

            path = os.path.join(SNAPSHOTS, file)
            image.save(f"{path}.png")
        else:
            QMessageBox.warning(self, "No image", "No image to save.")


class Rack(QRect):
    def __init__(self, *args, url: str = ""):
        super().__init__(*args)

        self.url = url
        self.sent = False


class VideoLabel(QLabel):
    def __init__(self, text: str, _):
        super().__init__(text)

        self._ = _

        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

        racks = RACKS.get(_, {})

        if not racks:
            RACKS[_] = {}

        self.racks: list[Rack] = [
            Rack(*rect["rect"], url=rect["url"]) for rect in racks.get("racks", [])
        ]
        self.drawing = False
        self.startPoint = None

    def paintEvent(self, event):
        super().paintEvent(event)

        painter = QPainter(self)
        painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
        painter.setFont(QFont("Arial", 12))
        # painter.setPen(Qt.black)

        for rect in self.racks:
            painter.drawRect(rect)
            painter.drawText(
                rect.adjusted(5, 5, -5, -5),
                Qt.TextWrapAnywhere | Qt.AlignBottom | Qt.AlignLeft,
                rect.url,
            )

        if self.drawing and self.startPoint:
            currentPoint = self.mapFromGlobal(QCursor.pos())
            rect = QRect(self.startPoint, currentPoint).normalized()
            painter.drawRect(rect)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.startPoint = self.mapFromGlobal(QCursor.pos())
            self.update()

        elif event.button() == Qt.RightButton:
            self.removeRectangle(event.pos())

    def mouseMoveEvent(self, event):
        if self.drawing:
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.drawing:
            endPoint = event.pos()
            rect = QRect(self.startPoint, endPoint).normalized()

            url, _ = QInputDialog.getText(
                self.window(),
                "Url",
                f"Enter url for this rack:",
            )
            if url:
                self.racks.append(Rack(rect, url=url))
                self.saveCoordinates()

            self.drawing = False
            self.startPoint = None
            self.update()

    def removeRectangle(self, pos):
        for rect in self.racks:
            if rect.contains(pos):
                self.racks.remove(rect)
                self.update()
                break

    def saveCoordinates(self):

        with open(COORDS, "w") as file:
            RACKS[self._].update(
                racks=[dict(rect=rect.getRect(), url=rect.url) for rect in self.racks]
            )
            json.dump(RACKS, file)

    def onLocationsReady(self, locations: list[list[int]]):
        for x1, y1, x2, y2 in locations:
            cow_midpoint = (x1 + x2) // 2, (y1 + y2) // 2

            for index, rack in enumerate(self.racks):
                if not rack.sent:
                    rack_midpoint = (rack.left() + rack.right()) // 2, (
                        rack.top() + rack.bottom()
                    ) // 2

                    if (rack.left() <= cow_midpoint[0] <= rack.top()) and (
                        rack.right() <= cow_midpoint[1] <= rack.bottom()
                    ):
                        if cow_midpoint[1] > rack_midpoint[1]:
                            threading.Thread(
                                target=self.send_api_get_request,
                                args=[rack],
                            ).start()

    def send_api_get_request(self, rack: Rack):
        rack.sent = True
        return

        print("SENDING REQUEST TO URL: ", rack.url)

        try:
            response = requests.get(rack.url)

            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                print("GET request successful.")
                print("Response content:")
                print(response.text)
            else:
                print(f"Error: {response.status_code} - {response.text}")

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}\n'{rack.url}'")
            return False

        return True


class VideoFeedFrame(VFrame):
    started = Signal()
    stopped = Signal()

    def __init__(self, win: "VideoNConfig", _):
        super().__init__()

        self.win = win

        self.image: QImage = None

        self.videoThread: VideoThread = None

        self.videoLabel = VideoLabel("Monitoring", _)
        self.addWidget(self.videoLabel)

        self.spinner = PRMP_QSpinner(self)

    def startVideoThread(self, rtspLink: Union[str, int], model: str):
        self.videoThread = VideoThread(rtspLink, model)
        self.videoThread.conf = (
            self.win.configFrame.confBar.value()
            / self.win.configFrame.confBar.maximum()
        )

        self.videoThread.imageReady.connect(self.onImageReady)
        self.videoThread.locationsReady.connect(self.videoLabel.onLocationsReady)

        self.videoThread.started.connect(self.started.emit)
        self.videoThread.finished.connect(self.stopped.emit)
        self.videoThread.destroyed.connect(self.stopped.emit)

        self.spinner.start()

        self.videoThread.start()

    def stopVideoThread(self):
        if self.videoThread:
            self.videoThread.stop()

    def onImageReady(self, image: QImage):
        if self.spinner._isSpinning:
            self.spinner.stop()

        self.image = image
        size = self.videoLabel.size()
        pixmap = QPixmap(image.smoothScaled(size.width(), size.height()))
        self.videoLabel.setPixmap(pixmap)


class VideoNConfig(VFrame):
    def __init__(self, win, _):
        super().__init__()

        self.win = win

        self.videoFeedFrame = VideoFeedFrame(self, _)
        self.configFrame = ConfigFrame(self, _)

        self.addWidget(self.videoFeedFrame, 1)
        self.addWidget(self.configFrame, 1)

    def closeEvent(self, _):
        self.videoFeedFrame.stopVideoThread()

    def addFeed(self):
        self.win.addFeed()


class Login(VFrame):
    def __init__(self, win):
        super().__init__()

        self.win = win

        self.addStretch()

        self.addWidget(QLabel("Login"), 0, Qt.AlignmentFlag.AlignCenter)
        self.addSpacing(20)

        self.username = QLineEdit()
        self.username.setPlaceholderText("Enter username")
        self.addWidget(self.username, 0, Qt.AlignmentFlag.AlignCenter)

        self.addSpacing(10)

        self.password = QLineEdit()
        self.password.setEchoMode(self.password.Password)
        self.password.setPlaceholderText("Enter password")
        self.addWidget(self.password, 0, Qt.AlignmentFlag.AlignCenter)

        self.addSpacing(10)

        login = QPushButton("Login")
        login.clicked.connect(self.login)
        self.addWidget(login, 0, Qt.AlignmentFlag.AlignCenter)

        self.addStretch()

    def login(self):
        if self.username.text() == "admin" and self.password.text() == "1234":
            self.win.showFrame()
        else:
            QMessageBox.warning(
                self,
                "Invalid credentials",
                "The provided login details are not correct",
            )


class Window(VFrame):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Cow Monitoring")

        self.login = Login(self)
        self.addWidget(self.login)

        self.zero = VideoNConfig(self, "0")
        self.zero.hide()
        self.addWidget(self.zero)

        self.videos: list[VideoNConfig] = [self.zero]

        self.showMaximized()

    def showFrame(self):
        self.login.hide()
        self.zero.show()

    def addFeed(self):
        new = VideoNConfig(self, str(len(self.videos)))
        self.videos.append(new)
        new.showMaximized()

    # def showEvent(self, _):
    #     self.setFixedSize(self.screen().size())


if __name__ == "__main__":
    os.system("python app.py")
