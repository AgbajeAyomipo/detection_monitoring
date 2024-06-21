from typing import Union
from commons import *
import cv2
from ultralytics import YOLO


class VideoThread(QThread):
    imageReady = Signal(QImage)
    locationsReady = Signal(list)

    def __init__(self, rtspLink: Union[str, int], model: str):
        super().__init__()

        self.rtspLink = rtspLink
        self.model = YOLO(model)
        self.model.to("cuda")
        self.conf: float = 0.4

        self.cap: cv2.VideoCapture = None

    def get_cow_locations(self, frame):
        results = self.model(frame, conf=self.conf, iou = .2)

        locations = []

        for r in results:
            boxes = r.boxes
            for box in boxes:
                b = box.xyxy[0]
                conf = round(box.conf[0].item(), 2)
                name = r.names[box.cls[0].item()]
                x1, y1, x2, y2 = (
                    int(b[0].item()),
                    int(b[1].item()),
                    int(b[2].item()),
                    int(b[3].item()),
                )

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(
                    frame,
                    f"{str(name)} {str(conf)}",
                    (x1, y1 - 5),
                    cv2.FONT_HERSHEY_COMPLEX_SMALL,
                    1.5,
                    (0, 255, 0),
                    1,
                )

                locations.append([x1, y1, x2, y2])

        return locations

    def run(self):
        self.cap = cv2.VideoCapture(self.rtspLink)
        while self.cap.isOpened():
            try:
                ret, frame = self.cap.read()
            except:
                continue

            if ret:
                locations = self.get_cow_locations(frame)

                height, width, _ = frame.shape
                bytesPerLine = 3 * width
                q_img = QImage(
                    frame.data,
                    width,
                    height,
                    bytesPerLine,
                    QImage.Format_RGB888,
                ).rgbSwapped()
                self.imageReady.emit(q_img)
                # self.imageReady.emit(self.add_rounded_corners(q_img))
                self.locationsReady.emit(locations)
            else:
                break
        self.cap.release()

    def add_rounded_corners(self, image):
        rounded_image = QImage(image.size(), QImage.Format_ARGB32)
        rounded_image.fill(Qt.transparent)

        painter = QPainter(rounded_image)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor(255, 25, 255, 255))
        painter.drawRoundedRect(rounded_image.rect(), 10, 10)
        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        painter.drawImage(0, 0, image)
        painter.end()

        return rounded_image

    def stop(self):
        if self.cap:
            self.cap.release()
        self.exit()


if __name__ == "__main__":
    os.system("python app.py")
