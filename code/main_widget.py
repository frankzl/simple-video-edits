from PyQt5.QtWidgets import *
from moviepy.editor import VideoFileClip
from PyQt5.QtGui import QPixmap, QImage


class MainWidget(QWidget):

    def __init__(self):

        super().__init__()
        self.video_path = None

        layout = QVBoxLayout()

        hlayout = QHBoxLayout()

        btn = QPushButton("Choose")
        btn.clicked.connect(self.get_path)
        self.selected_video = QLabel()
        self.selected_video.setText("Selected Video: None")

        hlayout.addWidget(self.selected_video)
        hlayout.addStretch()
        hlayout.addWidget(btn)

        layout.addLayout(hlayout)
        
        self.img_widget = ImageWidget()
        scroll = QScrollArea()
        scroll.setWidget(self.img_widget)
        layout.addWidget(scroll)

        
        self.setLayout(layout)
        self.setWindowTitle("Simple Video Edits")

    def get_path(self):
        self.video_path = QFileDialog.getOpenFileName(self, "")[0]
        self.video_clip = VideoFileClip(self.video_path)

        self.img_widget.set_frame(self.video_clip.get_frame(0))

        self.selected_video.setText( f"Selected Video: {self.video_path}")


class ImageWidget(QLabel):

    def __init__(self):
        super().__init__()
        self.pixmap = QPixmap()
        self.setPixmap(self.pixmap)
    
    def set_frame(self, frame):
        h,w,c = frame.shape
        #pixmap = QPixmap(QImage(frame, w, h, QImage.Format_RGB888))
        self.setPixmap(QPixmap.fromImage(QImage(frame, w, h, QImage.Format_RGB888)))
        self.setFixedWidth(w)
        self.setFixedHeight(h)

        print(frame.shape)

