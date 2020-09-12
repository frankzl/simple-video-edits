from PyQt5.QtWidgets import *
from moviepy.editor import VideoFileClip
from PyQt5.QtGui import QPixmap, QImage, QPainter, QColor
from PyQt5.QtCore import QEvent, QObject

from proglog import ProgressBarLogger

class MyProgressBarLogger(ProgressBarLogger):

    def __init__(self, qtprogressbar, max_value):
        super().__init__()

        self.qtprogressbar = qtprogressbar
        self.max_value = max_value

    def callback(self, **changes):
        # Every time the logger is updated, this function is called with
        # the `changes` dictionnary of the form `parameter: new value`.

        for (parameter, new_value) in changes.items():
            print ('Parameter %s is now %s' % (parameter, new_value))

    def bars_callback(self, bar, attr, value, old_value=None):
        self.qtprogressbar.setValue(round(100 * value/self.max_value, 2))

class MainWidget(QWidget):

    def __init__(self):

        super().__init__()
        self.save_path = ""
        self.video_path = None

        layout = QVBoxLayout()

        hlayout = QHBoxLayout()

        btn = QPushButton()
        btn.setIcon(self.style().standardIcon(getattr(QStyle, "SP_DialogOpenButton")))
        btn.clicked.connect(self.get_path)
        self.selected_video = QLabel()
        self.selected_video.setText("Selected Video: None")

        hlayout.addWidget(self.selected_video)
        hlayout.addStretch()
        hlayout.addWidget(btn)

        layout.addLayout(hlayout)
        
        self.selected_corner_points = QLabel("Select corner points: 1. top left, 2. bottom right")
        layout.addWidget(self.selected_corner_points)

        self.img_widget = ImageWidget(self)
        scroll = QScrollArea()
        scroll.setWidget(self.img_widget)

        layout.addWidget(scroll)

        hlayout = QHBoxLayout()
        self.save_path_label = QLabel("Save As: ")
        hlayout.addWidget( self.save_path_label )
        hlayout.addStretch()
        save_as_btn = QPushButton()
        save_as_btn.setIcon(self.style().standardIcon(getattr(QStyle, "SP_DialogOpenButton")))
        save_as_btn.clicked.connect(self.file_save)
        hlayout.addWidget( save_as_btn )

        layout.addLayout(hlayout)

        hlayout = QHBoxLayout()

        flayout = QFormLayout()
        self.fps_field = QLineEdit()
        self.fps_label = QLabel("fps: ")
        flayout.addRow( self.fps_label, self.fps_field)
        hlayout.addLayout(flayout)
        
        render_btn = QPushButton("Render")
        render_btn.clicked.connect(self.render_video)
        
        hlayout.addWidget(render_btn)
        
        layout.addLayout(hlayout)
        
        self.progressbar = QProgressBar()
        self.progressbar.setValue(0)
        self.progressbar.hide()
        layout.addWidget(self.progressbar)
        
        self.setLayout(layout)
        self.setWindowTitle("Simple Video Edits")

    def select_roi(self, img, roi):
        return img[roi[1]:roi[3], roi[0]:roi[2],:]

    def render_video(self):
        try:
            fps = (int((self.fps_field.text())))
            fps = fps if fps != -1 else None

            if not self.img_widget.selected_corners:
                roi = [(0,0), self.img_widget.image_size]
            else:
                roi = self.img_widget.selected_corners
            roi = list(roi[0]) + list(roi[1])

            if self.save_path == "":
                QMessageBox.about(self, "Error", f"Invalid Save Path")
                return
            
            output_clip = self.video_clip.fl_image(lambda img: self.select_roi(img, roi))
            self.progressbar.show()
            logger = MyProgressBarLogger(self.progressbar, 
                    (fps if fps else self.video_clip.fps)*self.video_clip.duration
            )
            output_clip.write_videofile(self.save_path, audio=False, fps=fps, logger=logger)
        except:
            QMessageBox.about(self, "Error", f"Invalid FPS or corners ({fps}, {roi})")
        
    def get_path(self):
        output = QFileDialog.getOpenFileName(self, "")
        self.video_path = output[0]
        
        try:
            self.video_clip = VideoFileClip(self.video_path)
            self.fps_label.setText(f"fps: (max {self.video_clip.fps:.2f}, type -1 for max fps)")
            self.img_widget.set_frame(self.video_clip.get_frame(0))
            self.selected_video.setText( f"Selected Video: {self.video_path}")
            self.progressbar.hide()
        except:
            QMessageBox.about(self, "Error", "Invalid Path.")

    def file_save(self):
        name = QFileDialog.getSaveFileName(self, 'Save File')[0]
        self.save_path_label.setText(f"Save As: {name}")
        if not name.lower().endswith("mp4"):
            QMessageBox.about(self, "Error", "Invalid Name. File should end with .mp4")
        else:
            self.save_path = name


    def update_rect(self):
        pt1,pt2 = self.img_widget.selected_corners

        self.selected_corner_points.setText(f"Select corner points: 1. top left, 2. bottom right ({pt1},{pt2})")

class ImageWidget(QLabel):

    def __init__(self, trigger_object):
        super().__init__()
        self.trigger_object = trigger_object
        self.pixmap = QPixmap()
        self.setPixmap(self.pixmap)
        self.setMouseTracking(True)
        self.image_size = None
        self.x, self.y = (0,0)
        self.selected_corners = []

        self.start_selection = False
    
    def set_frame(self, frame):
        h,w,c = frame.shape
        self.image_size = (w,h)
        self.pixmap = QPixmap.fromImage(QImage(frame, w, h, QImage.Format_RGB888))

        self.setPixmap(self.pixmap)
        self.setFixedWidth(w)
        self.setFixedHeight(h)

        self.trigger_object.selected_corner_points.setText(
                f"Select corner points: 1. top left, 2. bottom right - default ((0,0),{(w,h)})"
        )

    def paintEvent(self, e):
        if self.image_size:
            paint = QPainter()
            paint.begin(self)
            paint.drawPixmap(self.rect(), self.pixmap)
            paint.setPen(QColor(168, 34, 3, 127))

            w,h = self.image_size
            paint.drawLine(0, self.y, w,self.y)
            paint.drawLine(self.x, 0, self.x, h)

            #paint.setPen()
            if len(self.selected_corners) == 2:
                (x,y),(x2,y2) = self.selected_corners
                paint.fillRect( * self.compute_rect(x,y,x2,y2), QColor(0, 0, 255, 127) )

            elif len(self.selected_corners) == 1:
                (x,y) = self.selected_corners[0]
                paint.fillRect( * self.compute_rect(x,y,self.x,self.y), QColor(0, 0, 255, 127) )

            paint.end()

    def compute_rect(self, x1,y1,x2,y2):
        x = min(x1,x2)
        y = min(y1,y2)
        x_ = max(x1,x2)
        y_ = max(y1,y2)

        return (x,y,x_ - x, y_ - y)


    def mousePressEvent(self, ev):
        print(f"clicked {ev.x(), ev.y()}")
        self.start_selection = not(self.start_selection)
        if len(self.selected_corners) == 2:
            self.selected_corners = []
        self.selected_corners.append((ev.x(), ev.y()))
            
        if len(self.selected_corners) == 2: 
            w,h = self.image_size
            print((w,h))
            for idx,(x,y) in enumerate(self.selected_corners):
                if x < 6:
                    x = 0
                elif x > w - 6:
                    x = w
                if y < 6:
                    y = 0
                elif y >  h - 6:
                    y = h

                self.selected_corners[idx] = (x,y)

            self.trigger_object.update_rect()

    def mouseMoveEvent(self, ev):
        self.update()
        self.x = ev.x()
        self.y = ev.y()

